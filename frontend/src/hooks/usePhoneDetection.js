import { useEffect, useRef, useState } from 'react'
import { ObjectDetector, FilesetResolver } from '@mediapipe/tasks-vision'

const PHONE_LABELS = ['cell phone', 'mobile phone', 'phone', 'cellphone']
const DETECTION_INTERVAL_MS = 1000
const CONFIDENCE_THRESHOLD = 0.5
const PERSISTENCE_MS = 2000
const EVENT_COOLDOWN_MS = 15000
const WARNING_DISPLAY_MS = 5000

const MODEL_URLS = [
  'https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/float16/1/efficientdet_lite0.tflite',
  'https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/int8/1/efficientdet_lite0.tflite',
]

export default function usePhoneDetection({ stream, isActive, onDetected }) {
  const [phoneDetected, setPhoneDetected] = useState(false)
  const [initError, setInitError] = useState(null)
  const detectorRef = useRef(null)
  const videoRef = useRef(null)
  const rafRef = useRef(null)
  const timeoutRef = useRef(null)
  const runningRef = useRef(false)
  const sessionRef = useRef(0)
  const firstDetectionRef = useRef(null)
  const lastDetectionRef = useRef(null)
  const lastEventRef = useRef(0)
  const onDetectedRef = useRef(onDetected)

  useEffect(() => { onDetectedRef.current = onDetected }, [onDetected])

  useEffect(() => {
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

    const cleanup = () => {
      stopLoop()
      const video = videoRef.current
      videoRef.current = null
      if (video) {
        try { video.pause?.() } catch { /* ignore */ }
        try { video.srcObject = null } catch { /* ignore */ }
      }
      const detector = detectorRef.current
      detectorRef.current = null
      try { detector?.close?.() } catch { /* ignore */ }
    }

    const scheduleNext = (sessionId, fn) => {
      if (sessionId !== sessionRef.current || !runningRef.current) return
      if (typeof requestAnimationFrame === 'function') {
        rafRef.current = requestAnimationFrame(fn)
      } else {
        timeoutRef.current = setTimeout(() => fn(Date.now()), DETECTION_INTERVAL_MS)
      }
    }

    const loadModel = async (vision) => {
      let lastError = null
      for (const url of MODEL_URLS) {
        for (const delegate of ['GPU', 'CPU']) {
          try {
            const detector = await ObjectDetector.createFromOptions(vision, {
              baseOptions: {
                modelAssetPath: url,
                delegate,
              },
              scoreThreshold: CONFIDENCE_THRESHOLD,
              runningMode: 'VIDEO',
              maxResults: 10,
            })
            console.log(`[PhoneDetection] Model loaded successfully (delegate=${delegate})`)
            return detector
          } catch (err) {
            lastError = err
            console.warn(`[PhoneDetection] Failed to load model with delegate=${delegate}:`, err?.message || err)
          }
        }
      }
      throw lastError || new Error('All model load attempts failed')
    }

    const run = async () => {
      sessionRef.current += 1
      const sessionId = sessionRef.current
      cleanup()
      firstDetectionRef.current = null
      lastDetectionRef.current = null
      setPhoneDetected(false)
      setInitError(null)

      if (!isActive || !stream) {
        console.log('[PhoneDetection] Inactive or no stream, skipping')
        return
      }

      const videoTrack = stream.getVideoTracks?.()[0]
      if (!videoTrack || videoTrack.readyState !== 'live') {
        console.log('[PhoneDetection] No live video track, skipping')
        return
      }

      try {
        const vision = await FilesetResolver.forVisionTasks('/mediapipe/wasm')
        if (sessionId !== sessionRef.current) return

        const detector = await loadModel(vision)
        if (sessionId !== sessionRef.current) {
          try { detector.close() } catch { /* ignore */ }
          return
        }

        if (detectorRef.current) {
          try { detectorRef.current.close() } catch { /* ignore */ }
        }
        detectorRef.current = detector

        const video = document.createElement('video')
        video.autoplay = true
        video.playsInline = true
        video.muted = true
        video.srcObject = stream
        videoRef.current = video

        await new Promise((resolve, reject) => {
          let settled = false
          const ok = () => { if (!settled) { settled = true; resolve() } }
          const fail = () => { if (!settled) { settled = true; reject(new Error('video load failed')) } }
          video.onloadeddata = ok
          video.onloadedmetadata = ok
          video.onerror = fail
          if (video.readyState >= 2) ok()
          const playPromise = video.play?.()
          if (playPromise && typeof playPromise.catch === 'function') playPromise.catch(() => {})
          setTimeout(() => { if (!settled && video.readyState >= 2) ok() }, 1500)
        })

        if (sessionId !== sessionRef.current) return

        runningRef.current = true
        console.log('[PhoneDetection] Detection loop started')

        const detectLoop = (ts) => {
          if (sessionId !== sessionRef.current || !runningRef.current) return
          const det = detectorRef.current
          const v = videoRef.current
          if (!det || !v) return

          const now = typeof ts === 'number' ? ts : performance.now()

          try {
            if (v.readyState < 2 || !v.videoWidth || !v.videoHeight) {
              scheduleNext(sessionId, detectLoop)
              return
            }

            const result = det.detectForVideo(v, now)
            const detections = result?.detections || []

            // Log all unique labels seen (for debugging)
            if (detections.length > 0) {
              const labels = detections.map((d) => `${d.categories?.[0]?.categoryName} (${(d.categories?.[0]?.score || 0).toFixed(2)})`)
              console.log('[PhoneDetection] Detections:', labels.join(', '))
            }

            const phoneFound = detections.some((d) => {
              const category = d.categories?.[0]
              const label = (category?.categoryName || '').toLowerCase().replace(/[^a-z]/g, '')
              const score = category?.score || 0
              const isPhone = PHONE_LABELS.some((pl) => {
                const normalized = pl.replace(/[^a-z]/g, '')
                return label.includes(normalized) || normalized.includes(label)
              }) && score >= CONFIDENCE_THRESHOLD
              if (isPhone) {
                console.log('[PhoneDetection] Phone candidate found:', category?.categoryName, score)
              }
              return isPhone
            })

            if (phoneFound) {
              if (firstDetectionRef.current == null) {
                firstDetectionRef.current = Date.now()
              }
              lastDetectionRef.current = Date.now()
              const persisted = Date.now() - firstDetectionRef.current >= PERSISTENCE_MS
              if (persisted) {
                setPhoneDetected(true)
                const nowMs = Date.now()
                if (nowMs - lastEventRef.current >= EVENT_COOLDOWN_MS) {
                  lastEventRef.current = nowMs
                  console.log('[PhoneDetection] Phone confirmed, sending event')
                  try { onDetectedRef.current?.() } catch (e) { console.error('[PhoneDetection] Event callback error:', e) }
                }
              }
            } else {
              // Keep warning visible for at least WARNING_DISPLAY_MS after last detection
              const lastDet = lastDetectionRef.current
              if (lastDet && Date.now() - lastDet < WARNING_DISPLAY_MS) {
                // Keep phoneDetected true, don't reset
              } else {
                firstDetectionRef.current = null
                lastDetectionRef.current = null
                setPhoneDetected(false)
              }
            }
          } catch (err) {
            console.warn('[PhoneDetection] Detection frame error:', err?.message || err)
          }

          scheduleNext(sessionId, detectLoop)
        }

        scheduleNext(sessionId, detectLoop)
      } catch (err) {
        if (sessionId !== sessionRef.current) return
        console.error('[PhoneDetection] Initialization failed:', err?.message || err)
        setInitError(err?.message || 'Phone detection could not be initialized')
        cleanup()
      }
    }

    run()

    return () => {
      sessionRef.current += 1
      cleanup()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stream, isActive])

  return { phoneDetected, initError }
}
