/**
 * useBrowserProctoring
 *
 * Monitors browser-level proctoring signals during an active examination attempt:
 *   - Fullscreen exit     (fullscreenchange / webkitfullscreenchange)
 *   - Tab/window hidden   (visibilitychange)
 *   - Network offline     (offline / online)
 *
 * Events are queued in memory, deduplicated with a 2.5 s per-category cooldown,
 * and flushed to the backend via studentService.recordProctoringEvent().
 *
 * Design constraints
 * ------------------
 * - Each queued event stores the attemptId that was active when it was created.
 *   The flush always sends events to their own stored attemptId — never to a
 *   later one — and old-attempt events are cleared when the attemptId changes.
 * - 429 and 5xx errors are retried up to 3× with exponential back-off.
 * - Network errors (no HTTP status) are retried up to 3× with a 5 s delay.
 *   Only one pending retry timer exists at a time; it is cleared on cleanup.
 * - A flush generation token prevents stale async work (awaits/timers) from
 *   mutating queue state, releasing another flush's lock, or resuming after
 *   attempt change, deactivation, or unmount.
 * - React Strict Mode safe: cleanup removes all listeners and clears timers.
 * - setWarningNotice is never called after unmount.
 * - Camera, microphone, MediaPipe, and teacher-review are NOT handled here.
 * - The queue is in-memory only. Buffered events are lost if the page closes.
 * - Frontend throttling is supplementary; the backend rate-limiter is authoritative.
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import studentService from '../services/studentService';

// ── Constants ───────────────────────────────────────────────────────────────

/** Per-category minimum interval between queued events (ms). */
const COOLDOWN_MS = 2500;

/** Maximum events held in the in-memory queue. */
const MAX_QUEUE_SIZE = 50;

/**
 * Back-off delays (ms) for HTTP 429 and 5xx retries.
 * Up to RETRY_DELAYS.length retries are attempted; then the event is discarded.
 */
const RETRY_DELAYS = [1000, 2000, 4000];

/** Delay (ms) before retrying after a network error (no HTTP response). */
const NET_ERROR_RETRY_DELAY = 5000;

/** Maximum network-error retries before an event is discarded. */
const MAX_NET_RETRIES = 3;

// ── Helpers ─────────────────────────────────────────────────────────────────

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** True when the browser is in fullscreen, checking both standard and webkit APIs. */
function isCurrentlyFullscreen() {
  return !!(document.fullscreenElement || document.webkitFullscreenElement);
}

// ── Hook ────────────────────────────────────────────────────────────────────

/**
 * @param {object}      params
 * @param {string|null} params.attemptId  The active attempt ID.
 * @param {boolean}     params.isActive   True while the exam is in progress.
 *
 * @returns {{
 *   isFullscreen:   boolean,
 *   isOnline:       boolean,
 *   warningNotice:  string | null,
 *   clearWarning:   () => void,
 *   requestFullscreen: () => void,
 * }}
 */
export default function useBrowserProctoring({ attemptId, isActive }) {
  // ── Reactive state ────────────────────────────────────────────────────────
  const [isFullscreen, setIsFullscreen] = useState(isCurrentlyFullscreen);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [warningNotice, setWarningNotice] = useState(null);
  const [proctoringError, setProctoringError] = useState(null);

  // ── Refs ──────────────────────────────────────────────────────────────────

  /** Previous fullscreen state; guards against spurious initial-load events. */
  const wasFullscreenRef = useRef(isCurrentlyFullscreen());

  /** Previous visibility state; prevents duplicate tab-change events. */
  const wasHiddenRef = useRef(document.visibilityState === 'hidden');

  /**
   * Last emission timestamp per event_type.
   * Shape: { [eventType]: number }
   */
  const lastEmittedRef = useRef({});

  /**
   * In-memory event queue.
   * Each item: { attemptId, event_type, description, client_timestamp, _netRetries? }
   *
   * `attemptId` is stored with the event so the flush always sends it to the
   * correct attempt even if the prop changes between enqueue and flush.
   * `_netRetries` is an internal counter; it is not sent to the backend.
   */
  const queueRef = useRef([]);

  /** Prevents concurrent flush runs. */
  const isFlushingRef = useRef(false);

  /**
   * When true, monitoring has halted permanently for this attempt/session context.
   * Set by 401, 403, or 409 responses. Reset only when a new attempt is activated.
   */
  const stoppedRef = useRef(false);

  /**
   * Mirror of `attemptId` prop.
   * Written by a dedicated effect so async closures always read the latest value.
   */
  const attemptIdRef = useRef(attemptId);

  /**
   * Mirror of `isActive` prop.
   * Lets synchronous event handlers gate themselves without stale-closure risk.
   */
  const isActiveRef = useRef(isActive);

  /**
   * True while the component is mounted.
   * Guards async code (flushQueue) from calling setState after unmount.
   * Initialised to false; set to true inside the main effect.
   */
  const isMountedRef = useRef(false);

  /**
   * Handle for the pending network-error retry timer.
   * Only one timer is allowed at a time.
   */
  const retryTimerRef = useRef(null);

  /**
   * Flush generation/lifecycle token. Incremented on attempt change, deactivation,
   * unmount, or re-activation to invalidate in-flight flushes and pending timers.
   */
  const flushGenerationRef = useRef(0);

  /** Generation owned by the currently running flush, if any (for safe lock release). */
  const flushOwnerGenerationRef = useRef(null);

  const clearRetryTimer = useCallback(() => {
    if (retryTimerRef.current !== null) {
      clearTimeout(retryTimerRef.current);
      retryTimerRef.current = null;
    }
  }, []);

  const invalidateFlush = useCallback(() => {
    flushGenerationRef.current += 1;
    clearRetryTimer();
  }, [clearRetryTimer]);

  // ── Prop mirrors ──────────────────────────────────────────────────────────

  useEffect(() => {
    attemptIdRef.current = attemptId;
  }, [attemptId]);

  useEffect(() => {
    isActiveRef.current = isActive;
  }, [isActive]);

  // Attempt changes: purge old-attempt events, reset terminal state for the new
  // attempt, and invalidate any in-flight flush/timer from the previous attempt.
  useEffect(() => {
    queueRef.current = queueRef.current.filter((e) => e.attemptId === attemptId);
    stoppedRef.current = false;
    setProctoringError(null);
    invalidateFlush();
  }, [attemptId, invalidateFlush]);

  // ── Queue flush ───────────────────────────────────────────────────────────

  /**
   * Drain the queue, sending each event to its own stored attemptId.
   * - Concurrent calls are no-ops (isFlushingRef guard).
   * - Requires network connectivity and active monitoring; bails early otherwise.
   * - 429 and 5xx: up to 3 retries with exponential back-off, then discard.
   * - Network error: bounded retries via a delayed timer; item kept in queue.
   * - 401 / 403 / 409: stop monitoring, optionally warn user.
   * - 422 / other 4xx: discard immediately (bad payload, retrying is futile).
   * - Uses a generation token so stale async work cannot mutate queue state,
   *   release another flush's lock, or schedule/trigger stale retries.
   */
  const flushQueue = useCallback(async () => {
    if (isFlushingRef.current) return;
    if (!navigator.onLine) return;
    if (stoppedRef.current) return;
    if (!isActiveRef.current) return;

    const generation = flushGenerationRef.current;
    const isStale = () => generation !== flushGenerationRef.current;

    isFlushingRef.current = true;
    flushOwnerGenerationRef.current = generation;

    const removeExactItem = (target) => {
      const idx = queueRef.current.indexOf(target);
      if (idx !== -1) {
        queueRef.current.splice(idx, 1);
      }
    };

    try {
      while (queueRef.current.length > 0 && !stoppedRef.current) {
        if (isStale() || !isActiveRef.current) break;

        const item = queueRef.current[0]; // peek without removing
        if (!item) break;

        // A stale flush must not process events belonging to a different attempt.
        if (item.attemptId !== attemptIdRef.current) {
          break;
        }

        // Build the payload sent to the backend.
        // Internal fields (attemptId, _netRetries) are intentionally excluded.
        const payload = {
          event_type: item.event_type,
          description: item.description,
          client_timestamp: item.client_timestamp,
        };

        let succeeded = false;
        let discard = false;
        let stopProcessing = false;

        // Retry loop — handles 429 and 5xx with bounded back-off.
        for (let attempt = 0; attempt <= RETRY_DELAYS.length; attempt++) {
          if (isStale() || !isActiveRef.current) {
            stopProcessing = true;
            break;
          }

          try {
            await studentService.recordProctoringEvent(item.attemptId, payload);
            if (isStale()) {
              // Request may have completed after invalidation; server may have
              // recorded it. Remove only this exact event if still present to
              // avoid resend on resume. Never touch a replaced/new queue head.
              removeExactItem(item);
              stopProcessing = true;
              break;
            }
            succeeded = true;
            break;
          } catch (err) {
            if (isStale() || !isActiveRef.current) {
              stopProcessing = true;
              break;
            }

            const status = err?.response?.status;

            // ── 401 / 403: auth failure — halt monitoring ─────────────────
            if (status === 401 || status === 403) {
              stoppedRef.current = true;
              if (isMountedRef.current) {
                if (status === 401) {
                  setProctoringError(
                    'Proctoring monitoring paused due to a session/authentication error. Please sign in again if required.'
                  );
                  setWarningNotice(
                    'Proctoring monitoring has stopped due to an authentication error.'
                  );
                } else {
                  setProctoringError(
                    'Proctoring monitoring stopped due to an authorization error for this attempt.'
                  );
                  setWarningNotice(
                    'Proctoring monitoring has stopped due to an authorization error.'
                  );
                }
              }
              discard = true;
              break;
            }

            // ── 409: attempt ended — halt monitoring silently ─────────────
            if (status === 409) {
              stoppedRef.current = true;
              discard = true;
              break;
            }

            // ── 429 / 5xx: transient — retry with exponential back-off ────
            if (status === 429 || (status && status >= 500)) {
              if (attempt < RETRY_DELAYS.length) {
                await sleep(RETRY_DELAYS[attempt]);
                if (isStale() || !isActiveRef.current) {
                  stopProcessing = true;
                  break;
                }
                continue; // retry
              }
              // All retries exhausted — discard to unblock queue.
              discard = true;
              break;
            }

            // ── No status (network error / timeout / CORS abort) ──────────
            if (!status) {
              const retries = item._netRetries ?? 0;
              if (retries >= MAX_NET_RETRIES) {
                // Bounded retries exhausted — discard to unblock queue.
                discard = true;
              } else {
                item._netRetries = retries + 1;
                // Schedule exactly one delayed retry for this generation.
                // If a timer is already pending, let it run; don't stack another.
                if (retryTimerRef.current === null && !isStale() && isActiveRef.current) {
                  const scheduledGeneration = generation;
                  retryTimerRef.current = setTimeout(() => {
                    retryTimerRef.current = null;
                    if (
                      scheduledGeneration === flushGenerationRef.current &&
                      isActiveRef.current
                    ) {
                      flushQueue();
                    }
                  }, NET_ERROR_RETRY_DELAY);
                }
              }
              stopProcessing = true; // keep item at head; timer/new flush will retry
              break;
            }

            // ── 422 or other 4xx: bad payload — discard immediately ───────
            discard = true;
            break;
          }
        }

        if (stopProcessing) {
          break;
        }

        if (succeeded || discard) {
          // Remove only the exact event object that was processed.
          // If it no longer exists (e.g. removed by attempt change), do nothing.
          removeExactItem(item);
        }
      }
    } finally {
      // Only the owning flush may release the lock for its generation.
      if (flushOwnerGenerationRef.current === generation) {
        isFlushingRef.current = false;
        flushOwnerGenerationRef.current = null;
      }
    }
  }, []); // Stable — only reads refs; no prop dependencies.

  // ── Event enqueue ─────────────────────────────────────────────────────────

  const enqueueEvent = useCallback(
    (eventType, description) => {
      if (stoppedRef.current) return;
      if (!isActiveRef.current) return;

      // Per-category cooldown guard.
      const now = Date.now();
      if (now - (lastEmittedRef.current[eventType] ?? 0) < COOLDOWN_MS) return;
      lastEmittedRef.current[eventType] = now;

      // Drop oldest item when queue is full (capacity management, not async removal).
      if (queueRef.current.length >= MAX_QUEUE_SIZE) {
        queueRef.current.shift();
      }

      // Store the current attemptId with the event.
      queueRef.current.push({
        attemptId: attemptIdRef.current,
        event_type: eventType,
        description,
        client_timestamp: new Date().toISOString(),
      });

      flushQueue();
    },
    [flushQueue]
  );

  // ── Browser event handlers ────────────────────────────────────────────────

  /**
   * Shared handler for `fullscreenchange` and `webkitfullscreenchange`.
   * Uses wasFullscreenRef to detect genuine exit transitions; prevents
   * duplicate events when both events fire in the same browser.
   */
  const handleFullscreenChange = useCallback(() => {
    const nowFullscreen = isCurrentlyFullscreen();

    if (wasFullscreenRef.current && !nowFullscreen) {
      // Genuine fullscreen → non-fullscreen transition.
      enqueueEvent('fullscreen_exited', 'Candidate exited fullscreen mode');
      if (isMountedRef.current) {
        setWarningNotice(
          'You have exited fullscreen mode. Please return to fullscreen to continue.'
        );
      }
    }

    // Update ref AFTER the conditional so both events (standard + webkit)
    // read the same previous state on first fire, then see the updated state
    // on second fire — preventing a duplicate event emission.
    wasFullscreenRef.current = nowFullscreen;
    if (isMountedRef.current) {
      setIsFullscreen(nowFullscreen);
    }
  }, [enqueueEvent]);

  const handleVisibilityChange = useCallback(() => {
    if (document.visibilityState === 'hidden' && !wasHiddenRef.current) {
      wasHiddenRef.current = true;
      enqueueEvent(
        'tab_visibility_changed',
        'Candidate switched tabs or minimized the window'
      );
      if (isMountedRef.current) {
        setWarningNotice(
          'Tab switch or window minimization detected. Please remain on the examination tab.'
        );
      }
    } else if (document.visibilityState === 'visible') {
      wasHiddenRef.current = false;
    }
  }, [enqueueEvent]);

  const handleOffline = useCallback(() => {
    if (isMountedRef.current) {
      setIsOnline(false);
      setWarningNotice(
        'Network connection interrupted. Monitoring events will be queued until you are back online.'
      );
    }
    enqueueEvent('network_interrupted', 'Network connection lost');
  }, [enqueueEvent]);

  const handleOnline = useCallback(() => {
    if (isMountedRef.current) {
      setIsOnline(true);
    }
    flushQueue(); // drain events buffered while offline
  }, [flushQueue]);

  // ── Main effect: attach / detach listeners ────────────────────────────────

  useEffect(() => {
    // Mark as mounted so async flushQueue can safely call setState.
    isMountedRef.current = true;

    if (!isActive) {
      // Exam not active — stop transmissions/timers and ensure no listeners linger.
      // Do not clear the queue here: same-attempt deactivation/reactivation must
      // preserve valid queued events. Attempt-specific purging is handled by the
      // attemptId change effect.
      invalidateFlush();
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('online', handleOnline);
      return () => {
        // Invalidate any async work from this setup before unmount/Strict Mode cleanup.
        invalidateFlush();
        isMountedRef.current = false;
      };
    }

    // ── Active session setup ──────────────────────────────────────────────

    // Invalidate stale async work/timers from a previous setup or inactive period.
    invalidateFlush();

    // Preserve events for the same attempt; remove any that do not belong.
    queueRef.current = queueRef.current.filter((e) => e.attemptId === attemptId);

    // Do not reset stoppedRef here: reactivating the same attempt after a
    // terminal 401/403/409 must remain stopped. A new attempt resets terminal
    // state in the attemptId change effect above.

    // Sync initial UI state to real browser conditions.
    const currentlyFullscreen = isCurrentlyFullscreen();
    wasFullscreenRef.current = currentlyFullscreen;
    setIsFullscreen(currentlyFullscreen);

    wasHiddenRef.current = document.visibilityState === 'hidden';
    setIsOnline(navigator.onLine);

    // Attach listeners — both standard and webkit for fullscreen.
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('offline', handleOffline);
    window.addEventListener('online', handleOnline);

    return () => {
      // Invalidate before cleanup so stale timer callbacks/flushes cannot proceed.
      invalidateFlush();
      isMountedRef.current = false;
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('online', handleOnline);
    };
  }, [
    isActive,
    attemptId,
    handleFullscreenChange,
    handleVisibilityChange,
    handleOffline,
    handleOnline,
    invalidateFlush,
  ]);

  // ── Public API ────────────────────────────────────────────────────────────

  const clearWarning = useCallback(() => setWarningNotice(null), []);

  const requestFullscreen = useCallback(() => {
    const el = document.documentElement;
    try {
      if (el.requestFullscreen) {
        // Must be called from a user-gesture handler (e.g. onClick).
        el.requestFullscreen().catch(() => {
          // Browser denied or policy blocked — ignore.
        });
      } else if (el.webkitRequestFullscreen) {
        // Safari fallback.
        el.webkitRequestFullscreen();
      }
    } catch {
      // Browser denied or policy blocked — ignore.
    }
  }, []);

  return {
    isFullscreen,
    isOnline,
    warningNotice,
    proctoringError,
    clearWarning,
    requestFullscreen,
  };
}
