import { useEffect, useRef } from 'react'
import { FACE_DETECTION_STATUS } from '../../hooks/useFaceDetection'

function faceStatusLabel(status) {
  switch (status) {
    case FACE_DETECTION_STATUS.INITIALIZING:
      return 'Initializing detector'
    case FACE_DETECTION_STATUS.DETECTED:
      return 'Face detected'
    case FACE_DETECTION_STATUS.NOT_DETECTED:
      return 'No face detected'
    case FACE_DETECTION_STATUS.MULTIPLE:
      return 'Multiple faces detected'
    case FACE_DETECTION_STATUS.LOOKING_AWAY:
      return 'Please look towards the screen'
    case FACE_DETECTION_STATUS.GAZE_UNAVAILABLE:
      return 'Looking-direction detection unavailable'
    case FACE_DETECTION_STATUS.UNAVAILABLE:
      return 'Detection unavailable'
    case FACE_DETECTION_STATUS.ERROR:
      return 'Detection error'
    default:
      return 'Initializing detector'
  }
}

function faceStatusClasses(status) {
  if (status === FACE_DETECTION_STATUS.DETECTED) return 'bg-green-100 text-green-800 border-green-200'
  if (status === FACE_DETECTION_STATUS.INITIALIZING) return 'bg-blue-50 text-blue-800 border-blue-200'
  if (
    status === FACE_DETECTION_STATUS.NOT_DETECTED ||
    status === FACE_DETECTION_STATUS.MULTIPLE ||
    status === FACE_DETECTION_STATUS.LOOKING_AWAY
  ) {
    return 'bg-amber-100 text-amber-900 border-amber-200'
  }
  return 'bg-gray-100 text-gray-800 border-gray-200'
}

/**
 * Small live camera preview for the examination screen.
 * Uses a shared MediaStream from context (no new getUserMedia calls).
 * Optionally displays face detection and head-orientation status.
 */
export default function ExamCameraPreview({ stream, faceStatus, faceMessage }) {
  const videoRef = useRef(null)

  useEffect(() => {
    const video = videoRef.current
    if (!video) return
    if (stream) {
      video.srcObject = stream
      const playPromise = video.play?.()
      if (playPromise && typeof playPromise.catch === 'function') {
        playPromise.catch(() => {})
      }
    } else {
      video.srcObject = null
    }
    return () => {
      if (video) video.srcObject = null
    }
  }, [stream])

  const status = faceStatus || FACE_DETECTION_STATUS.INITIALIZING
  const label = faceStatusLabel(status)

  return (
    <div className="flex flex-col items-start sm:items-end gap-1">
      <div className="w-40 h-28 sm:w-48 sm:h-32 bg-[var(--color-surface-soft)] border border-[var(--color-border)] rounded-lg overflow-hidden shadow-sm flex items-center justify-center relative">
        {stream ? (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
            aria-label="Live camera monitoring preview"
          />
        ) : (
          <span className="text-[10px] text-[var(--color-text-muted)] text-center px-2">
            Camera unavailable
          </span>
        )}
        <span className={`absolute bottom-1 left-1 right-1 text-[10px] leading-tight px-1.5 py-0.5 rounded border ${faceStatusClasses(status)}`}>
          {label}
        </span>
      </div>
      {faceMessage && status !== FACE_DETECTION_STATUS.DETECTED && status !== FACE_DETECTION_STATUS.INITIALIZING && (
        <p className="text-[10px] text-[var(--color-text-secondary)] max-w-[12rem] text-left sm:text-right">
          {faceMessage}
        </p>
      )}
    </div>
  )
}
