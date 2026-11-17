import { useEffect, useRef, useState } from 'react'
import { FaceLandmarker, FilesetResolver } from '@mediapipe/tasks-vision'

export const FACE_DETECTION_STATUS = {
  INITIALIZING: 'initializing',
  DETECTED: 'detected',
  NOT_DETECTED: 'not_detected',
  MULTIPLE: 'multiple',
  LOOKING_AWAY: 'looking_away',
  GAZE_UNAVAILABLE: 'gaze_unavailable',
  UNAVAILABLE: 'unavailable',
  ERROR: 'error',
}

/**
 * Configurable thresholds for stable face/presence/orientation detection.
 * Orientation is basic head-pose estimation from facial transformation matrices,
 * not exact eye-gaze tracking.
 */
const DETECTION_INTERVAL_MS = 400
const MIN_FACE_CONFIDENCE = 0.5
const NO_FACE_PERSIST_MS = 2500
const MULTIPLE_PERSIST_MS = 1500
const CLEAR_PERSIST_MS = 800
const EVENT_COOLDOWN_MS = 12000

// Conservative head-orientation thresholds (degrees) and persistence windows.
const LOOKING_AWAY_YAW_DEG = 25
const LOOKING_AWAY_PITCH_DEG = 20
const LOOKING_AWAY_PERSIST_MS = 3000
const LOOKING_AWAY_CLEAR_MS = 1000

function countFaces(result) {
  const faces = result?.faceLandmarks
  if (!Array.isArray(faces)) return 0
  return faces.length
}

function createDetectorVideo(stream) {
  const video = document.createElement('video')
  video.autoplay = true
  video.playsInline = true
  video.muted = true
  video.srcObject = stream
  return video
}

/**
 * Estimate head orientation (yaw/pitch in degrees) from MediaPipe's 4x4 facial
 * transformation matrix (column-major). This is approximate head orientation only.
 * Returns null if matrix data is unavailable/invalid.
 */
function estimateHeadOrientationDegrees(result) {
  const matrices = result?.facialTransformationMatrixes
  if (!Array.isArray(matrices) || matrices.length === 0) return null
  const matrix = matrices[0]
  const data = matrix?.data || matrix
  if (!data || data.length < 16) return null

  const m = data
  // Column-major: m[col*4 + row]
  const r00 = m[0], r10 = m[1], r20 = m[2]
  const r01 = m[4], r11 = m[5], r21 = m[6]
  const r02 = m[8], r12 = m[9], r22 = m[10]

  // Derive pitch/yaw from rotation components (approximate, degrees).
  const pitchRad = Math.atan2(-r12, Math.sqrt(r02 * r02 + r22 * r22))
  const yawRad = Math.atan2(r02, r22)
  // Roll available if needed: Math.atan2(r10, r11)
  const pitchDeg = (pitchRad * 180) / Math.PI
  const yawDeg = (yawRad * 180) / Math.PI

  if (!Number.isFinite(pitchDeg) || !Number.isFinite(yawDeg)) return null
  return { yawDeg, pitchDeg }
}

function isHeadTurnedAway(orientation) {
  if (!orientation) return false
  return Math.abs(orientation.yawDeg) > LOOKING_AWAY_YAW_DEG || Math.abs(orientation.pitchDeg) > LOOKING_AWAY_PITCH_DEG
}

export default function useFaceDetection({
  attemptId,
  stream,
  isActive,
  onProctoringEvent,
  onStatusChange,
}) {
  const [status, setStatus] = useState(FACE_DETECTION_STATUS.INITIALIZING)
  const [message, setMessage] = useState('Initializing face detection…')

  const landmarkerRef = useRef(null)
  const videoRef = useRef(null)
  const rafRef = useRef(null)
  const timeoutRef = useRef(null)
  const runningRef = useRef(false)
  const sessionRef = useRef(0)
  const lastDetectTimeRef = useRef(0)
  const lastEventAtRef = useRef({ face_not_detected: 0, multiple_faces_detected: 0, looking_away: 0 })
  const conditionStartRef = useRef({ no_face: null, multiple: null, ok: null })
  const lookingAwayStartRef = useRef(null)
  const lookingNormalStartRef = useRef(null)
  const sustainedLookingAwayRef = useRef(false)
  const gazeAvailableRef = useRef(false)
  const onEventRef = useRef(onProctoringEvent)
  const onStatusRef = useRef(onStatusChange)

  useEffect(() => { onEventRef.current = onProctoringEvent }, [onProctoringEvent])
  useEffect(() => { onStatusRef.current = onStatusChange }, [onStatusChange])

  useEffect(() => {
    const emitStatus = (nextStatus, nextMessage) => {
      setStatus(nextStatus)
      setMessage(nextMessage)
      onStatusRef.current?.(nextStatus, nextMessage)
    }

    const stopLoop = () => {
      runningRef.current = false
      if (rafRef.current != null) {
        cancelAnimationFrame(rafRef.current)
        rafRef.current = null
      }
      if (timeoutRef.current != null) {
        clearTimeout(timeoutRef.current)
        timeoutRef.current = null
      }
    }

    const cleanupDetector = () => {
      stopLoop()
      const video = videoRef.current
      videoRef.current = null
      if (video) {
        try {
          video.pause?.()
        } catch { /* ignore */ }
        try {
          video.srcObject = null
        } catch { /* ignore */ }
      }
      const landmarker = landmarkerRef.current
      landmarkerRef.current = null
      try {
        landmarker?.close?.()
      } catch { /* ignore */ }
    }

    const maybeEmitEvent = (eventType, description) => {
      const now = Date.now()
      const last = lastEventAtRef.current[eventType] || 0
      if (now - last < EVENT_COOLDOWN_MS) return
      lastEventAtRef.current[eventType] = now
      try {
        onEventRef.current?.({
          event_type: eventType,
          description,
        })
      } catch {
        // Event reporting must not break detection.
      }
    }

    const scheduleNext = (sessionId, fn) => {
      if (sessionId !== sessionRef.current || !runningRef.current) return
      if (typeof requestAnimationFrame === 'function') {
        rafRef.current = requestAnimationFrame(fn)
      } else {
        timeoutRef.current = setTimeout(() => fn(Date.now()), DETECTION_INTERVAL_MS)
      }
    }

    const resetGazeState = () => {
      lookingAwayStartRef.current = null
      lookingNormalStartRef.current = null
      sustainedLookingAwayRef.current = false
    }

    const createLandmarkerWithFallback = async (vision, sessionId) => {
      const baseConfig = {
        baseOptions: {
          modelAssetPath: '/mediapipe/models/face_landmarker.task',
        },
        runningMode: 'VIDEO',
        numFaces: 2,
        minFaceDetectionConfidence: MIN_FACE_CONFIDENCE,
        minFacePresenceConfidence: MIN_FACE_CONFIDENCE,
        minTrackingConfidence: MIN_FACE_CONFIDENCE,
        outputFaceBlendshapes: false,
        outputFacialTransformationMatrixes: true,
      }

      const tryCreate = async (delegate) => {
        const lm = await FaceLandmarker.createFromOptions(vision, {
          ...baseConfig,
          baseOptions: { ...baseConfig.baseOptions, delegate },
        })
        return lm
      }

      // Prefer GPU, fall back to CPU if initialization fails (supported by package).
      try {
        return await tryCreate('GPU')
      } catch (gpuErr) {
        if (sessionId !== sessionRef.current) throw gpuErr
        try {
          return await tryCreate('CPU')
        } catch (cpuErr) {
          throw cpuErr || gpuErr
        }
      }
    }

    const run = async () => {
      sessionRef.current += 1
      const sessionId = sessionRef.current
      cleanupDetector()
      lastEventAtRef.current = { face_not_detected: 0, multiple_faces_detected: 0, looking_away: 0 }
      conditionStartRef.current = { no_face: null, multiple: null, ok: null }
      resetGazeState()
      gazeAvailableRef.current = false
      lastDetectTimeRef.current = 0

      if (!isActive || !attemptId) {
        emitStatus(FACE_DETECTION_STATUS.UNAVAILABLE, 'Face detection inactive.')
        return
      }
      if (!stream) {
        emitStatus(FACE_DETECTION_STATUS.UNAVAILABLE, 'Camera stream unavailable.')
        return
      }

      const videoTrack = stream.getVideoTracks?.()[0]
      if (!videoTrack || videoTrack.readyState !== 'live') {
        emitStatus(FACE_DETECTION_STATUS.UNAVAILABLE, 'Camera track unavailable.')
        return
      }

      if (typeof window === 'undefined' || typeof document === 'undefined') {
        emitStatus(FACE_DETECTION_STATUS.ERROR, 'Face detection unavailable in this environment.')
        return
      }
      if (!navigator?.mediaDevices) {
        emitStatus(FACE_DETECTION_STATUS.ERROR, 'Media devices are not supported in this browser.')
        return
      }

      emitStatus(FACE_DETECTION_STATUS.INITIALIZING, 'Initializing face detection…')

      try {
        const vision = await FilesetResolver.forVisionTasks('/mediapipe/wasm')
        if (sessionId !== sessionRef.current) return

        const landmarker = await createLandmarkerWithFallback(vision, sessionId)
        if (sessionId !== sessionRef.current) {
          try { landmarker.close() } catch { /* ignore */ }
          return
        }
        // Guard against duplicate active instances for this session.
        if (landmarkerRef.current) {
          try { landmarkerRef.current.close() } catch { /* ignore */ }
        }
        landmarkerRef.current = landmarker

        const video = createDetectorVideo(stream)
        videoRef.current = video

        await new Promise((resolve, reject) => {
          let settled = false
          const cleanup = () => {
            video.onloadeddata = null
            video.onloadedmetadata = null
            video.onerror = null
          }
          const ok = () => {
            if (settled) return
            settled = true
            cleanup()
            resolve()
          }
          const fail = (e) => {
            if (settled) return
            settled = true
            cleanup()
            reject(e || new Error('Video load failed'))
          }
          video.onloadeddata = ok
          video.onloadedmetadata = ok
          video.onerror = fail
          if (video.readyState >= 2) ok()
          const playPromise = video.play?.()
          if (playPromise && typeof playPromise.catch === 'function') {
            playPromise.catch(() => {})
          }
          setTimeout(() => {
            if (!settled && video.readyState >= 2) ok()
          }, 1500)
        })

        if (sessionId !== sessionRef.current) return

        runningRef.current = true
        emitStatus(FACE_DETECTION_STATUS.INITIALIZING, 'Starting face detection…')

        const detectLoop = (ts) => {
          if (sessionId !== sessionRef.current || !runningRef.current) return
          const lm = landmarkerRef.current
          const v = videoRef.current
          if (!lm || !v) return

          const now = typeof ts === 'number' ? ts : performance.now()
          if (now - lastDetectTimeRef.current < DETECTION_INTERVAL_MS) {
            scheduleNext(sessionId, detectLoop)
            return
          }
          lastDetectTimeRef.current = now

          try {
            if (v.readyState < 2 || !v.videoWidth || !v.videoHeight) {
              scheduleNext(sessionId, detectLoop)
              return
            }

            let result
            try {
              result = lm.detectForVideo(v, now)
            } catch {
              scheduleNext(sessionId, detectLoop)
              return
            }

            const faceCount = countFaces(result)
            const wallNow = Date.now()

            if (faceCount === 0) {
              conditionStartRef.current.ok = null
              conditionStartRef.current.multiple = null
              resetGazeState()
              gazeAvailableRef.current = false
              if (conditionStartRef.current.no_face == null) conditionStartRef.current.no_face = wallNow
              const persisted = wallNow - conditionStartRef.current.no_face >= NO_FACE_PERSIST_MS
              if (persisted) {
                emitStatus(FACE_DETECTION_STATUS.NOT_DETECTED, 'No face detected. Please stay clearly visible to the camera.')
                maybeEmitEvent('face_not_detected', 'No face detected for a sustained period during the examination.')
              }
            } else if (faceCount > 1) {
              conditionStartRef.current.ok = null
              conditionStartRef.current.no_face = null
              resetGazeState()
              gazeAvailableRef.current = false
              if (conditionStartRef.current.multiple == null) conditionStartRef.current.multiple = wallNow
              const persisted = wallNow - conditionStartRef.current.multiple >= MULTIPLE_PERSIST_MS
              if (persisted) {
                emitStatus(FACE_DETECTION_STATUS.MULTIPLE, 'Multiple faces detected. Please ensure only you are visible.')
                maybeEmitEvent('multiple_faces_detected', 'Multiple faces detected in the camera view for a sustained period.')
              }
            } else {
              // Exactly one face: allow gaze/head-orientation evaluation.
              conditionStartRef.current.no_face = null
              conditionStartRef.current.multiple = null
              if (conditionStartRef.current.ok == null) conditionStartRef.current.ok = wallNow
              const faceStable = wallNow - conditionStartRef.current.ok >= CLEAR_PERSIST_MS

              const orientation = estimateHeadOrientationDegrees(result)
              const hasOrientation = orientation != null
              gazeAvailableRef.current = hasOrientation

              if (!hasOrientation) {
                // Face present but looking-direction estimation unavailable.
                resetGazeState()
                if (faceStable) {
                  emitStatus(FACE_DETECTION_STATUS.GAZE_UNAVAILABLE, 'Looking-direction detection unavailable.')
                }
              } else {
                const turnedAway = isHeadTurnedAway(orientation)
                if (turnedAway) {
                  lookingNormalStartRef.current = null
                  if (lookingAwayStartRef.current == null) lookingAwayStartRef.current = wallNow
                  const awayPersisted = wallNow - lookingAwayStartRef.current >= LOOKING_AWAY_PERSIST_MS
                  if (awayPersisted) {
                    if (!sustainedLookingAwayRef.current) {
                      sustainedLookingAwayRef.current = true
                      // Transition-based event: emit once on sustained classification (cooldown-guarded).
                      maybeEmitEvent('looking_away', 'Candidate head orientation was turned away from the screen for a sustained period.')
                    }
                    emitStatus(FACE_DETECTION_STATUS.LOOKING_AWAY, 'Please look towards the screen.')
                  } else {
                    // Brief movement: do not classify as looking away yet.
                    if (!sustainedLookingAwayRef.current && faceStable) {
                      emitStatus(FACE_DETECTION_STATUS.DETECTED, 'Face detected.')
                    }
                  }
                } else {
                  lookingAwayStartRef.current = null
                  if (sustainedLookingAwayRef.current) {
                    // Require ~1s of normal viewing direction before clearing warning.
                    if (lookingNormalStartRef.current == null) lookingNormalStartRef.current = wallNow
                    const normalPersisted = wallNow - lookingNormalStartRef.current >= LOOKING_AWAY_CLEAR_MS
                    if (normalPersisted) {
                      sustainedLookingAwayRef.current = false
                      lookingNormalStartRef.current = null
                      if (faceStable) {
                        emitStatus(FACE_DETECTION_STATUS.DETECTED, 'Face detected.')
                      }
                    } else {
                      emitStatus(FACE_DETECTION_STATUS.LOOKING_AWAY, 'Please look towards the screen.')
                    }
                  } else {
                    lookingNormalStartRef.current = null
                    if (faceStable) {
                      emitStatus(FACE_DETECTION_STATUS.DETECTED, 'Face detected.')
                    }
                  }
                }
              }
            }
          } catch {
            // Keep loop alive on unexpected per-frame errors.
          }

          scheduleNext(sessionId, detectLoop)
        }

        scheduleNext(sessionId, detectLoop)
      } catch (err) {
        if (sessionId !== sessionRef.current) return
        cleanupDetector()
        const msg = err?.message || 'Face detection could not be initialized.'
        emitStatus(FACE_DETECTION_STATUS.ERROR, `Face detection unavailable: ${msg}`)
      }
    }

    run()

    return () => {
      sessionRef.current += 1
      cleanupDetector()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [attemptId, stream, isActive])

  return { status, message }
}
