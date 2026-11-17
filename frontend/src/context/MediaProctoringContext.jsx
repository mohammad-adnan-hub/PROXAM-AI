import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react'

const MediaProctoringContext = createContext(null)

export const MEDIA_PERMISSION_STATUS = {
  IDLE: 'idle',
  REQUESTING: 'requesting',
  GRANTED: 'granted',
  DENIED: 'denied',
  UNAVAILABLE: 'unavailable',
  ERROR: 'error',
}

function stopStreamTracks(stream) {
  if (!stream) return
  stream.getTracks().forEach((track) => {
    try {
      track.stop()
    } catch {
      // ignore
    }
  })
}

export function MediaProctoringProvider({ children }) {
  const [stream, setStream] = useState(null)
  const [cameraStatus, setCameraStatus] = useState(MEDIA_PERMISSION_STATUS.IDLE)
  const [microphoneStatus, setMicrophoneStatus] = useState(MEDIA_PERMISSION_STATUS.IDLE)
  const [permissionError, setPermissionError] = useState('')
  const [devices, setDevices] = useState({ hasCamera: null, hasMicrophone: null })

  const streamRef = useRef(null)
  const mountedRef = useRef(true)

  useEffect(() => {
    mountedRef.current = true
    return () => {
      mountedRef.current = false
    }
  }, [])

  const stopMedia = useCallback(() => {
    const current = streamRef.current
    streamRef.current = null
    stopStreamTracks(current)
    if (mountedRef.current) {
      setStream(null)
    }
  }, [])

  const inspectDevices = useCallback(async () => {
    if (!navigator.mediaDevices?.enumerateDevices) {
      return { hasCamera: null, hasMicrophone: null }
    }
    try {
      const list = await navigator.mediaDevices.enumerateDevices()
      const hasCamera = list.some((d) => d.kind === 'videoinput')
      const hasMicrophone = list.some((d) => d.kind === 'audioinput')
      const result = { hasCamera, hasMicrophone }
      if (mountedRef.current) setDevices(result)
      return result
    } catch {
      const result = { hasCamera: null, hasMicrophone: null }
      if (mountedRef.current) setDevices(result)
      return result
    }
  }, [])

  const requestPermissions = useCallback(async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      if (mountedRef.current) {
        setCameraStatus(MEDIA_PERMISSION_STATUS.UNAVAILABLE)
        setMicrophoneStatus(MEDIA_PERMISSION_STATUS.UNAVAILABLE)
        setPermissionError('Camera and microphone are not supported in this browser.')
      }
      return { ok: false, stream: null }
    }

    // Stop any existing stream before requesting a new one to avoid duplicates.
    stopMedia()

    if (mountedRef.current) {
      setPermissionError('')
      setCameraStatus(MEDIA_PERMISSION_STATUS.REQUESTING)
      setMicrophoneStatus(MEDIA_PERMISSION_STATUS.REQUESTING)
    }

    const deviceInfo = await inspectDevices()

    try {
      const newStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      })

      if (!mountedRef.current) {
        stopStreamTracks(newStream)
        return { ok: false, stream: null }
      }

      streamRef.current = newStream
      setStream(newStream)

      const videoTracks = newStream.getVideoTracks()
      const audioTracks = newStream.getAudioTracks()

      const camGranted = videoTracks.length > 0
      const micGranted = audioTracks.length > 0

      setCameraStatus(camGranted ? MEDIA_PERMISSION_STATUS.GRANTED : MEDIA_PERMISSION_STATUS.UNAVAILABLE)
      setMicrophoneStatus(micGranted ? MEDIA_PERMISSION_STATUS.GRANTED : MEDIA_PERMISSION_STATUS.UNAVAILABLE)

      if (!camGranted || !micGranted) {
        setPermissionError('Camera or microphone track could not be started. Please check your devices and try again.')
        // If required media missing, stop partial stream.
        stopStreamTracks(newStream)
        streamRef.current = null
        setStream(null)
        return { ok: false, stream: null }
      }

      // Keep device info updated after grant (labels may become available).
      inspectDevices()

      // Handle track ending/disconnect.
      const onTrackEnded = () => {
        if (!mountedRef.current) return
        const current = streamRef.current
        if (!current) return
        const hasLiveVideo = current.getVideoTracks().some((t) => t.readyState === 'live')
        const hasLiveAudio = current.getAudioTracks().some((t) => t.readyState === 'live')
        if (!hasLiveVideo) setCameraStatus(MEDIA_PERMISSION_STATUS.UNAVAILABLE)
        if (!hasLiveAudio) setMicrophoneStatus(MEDIA_PERMISSION_STATUS.UNAVAILABLE)
        if (!hasLiveVideo || !hasLiveAudio) {
          setPermissionError('A required device was disconnected. Please reconnect and retry.')
          stopStreamTracks(current)
          streamRef.current = null
          setStream(null)
        }
      }

      videoTracks.forEach((t) => { t.onended = onTrackEnded })
      audioTracks.forEach((t) => { t.onended = onTrackEnded })

      return { ok: true, stream: newStream }
    } catch (err) {
      if (!mountedRef.current) return { ok: false, stream: null }

      const name = err?.name || ''
      const isDenied = name === 'NotAllowedError' || name === 'PermissionDeniedError' || name === 'SecurityError'
      const isNotFound = name === 'NotFoundError' || name === 'DevicesNotFoundError'
      const isNotReadable = name === 'NotReadableError' || name === 'TrackStartError'
      const isOverconstrained = name === 'OverconstrainedError' || name === 'ConstraintNotSatisfiedError'

      if (isDenied) {
        setCameraStatus(MEDIA_PERMISSION_STATUS.DENIED)
        setMicrophoneStatus(MEDIA_PERMISSION_STATUS.DENIED)
        setPermissionError('Camera and microphone permissions were denied. Please allow access in your browser settings and retry.')
      } else if (isNotFound) {
        setCameraStatus(deviceInfo.hasCamera === false ? MEDIA_PERMISSION_STATUS.UNAVAILABLE : MEDIA_PERMISSION_STATUS.ERROR)
        setMicrophoneStatus(deviceInfo.hasMicrophone === false ? MEDIA_PERMISSION_STATUS.UNAVAILABLE : MEDIA_PERMISSION_STATUS.ERROR)
        setPermissionError('Required camera or microphone was not found. Please connect your devices and retry.')
      } else if (isNotReadable) {
        setCameraStatus(MEDIA_PERMISSION_STATUS.ERROR)
        setMicrophoneStatus(MEDIA_PERMISSION_STATUS.ERROR)
        setPermissionError('Camera or microphone is already in use or could not be started. Close other apps using them and retry.')
      } else if (isOverconstrained) {
        setCameraStatus(MEDIA_PERMISSION_STATUS.ERROR)
        setMicrophoneStatus(MEDIA_PERMISSION_STATUS.ERROR)
        setPermissionError('Camera or microphone constraints could not be satisfied on this device.')
      } else {
        setCameraStatus(MEDIA_PERMISSION_STATUS.ERROR)
        setMicrophoneStatus(MEDIA_PERMISSION_STATUS.ERROR)
        setPermissionError(err?.message || 'Could not access camera and microphone. Please try again.')
      }

      return { ok: false, stream: null }
    }
  }, [inspectDevices, stopMedia])

  // Do not auto-request on mount. Stop on provider unmount (leaving attempt flow).
  useEffect(() => {
    return () => {
      const current = streamRef.current
      streamRef.current = null
      stopStreamTracks(current)
    }
  }, [])

  const value = useMemo(() => ({
    stream,
    cameraStatus,
    microphoneStatus,
    permissionError,
    devices,
    requestPermissions,
    stopMedia,
    inspectDevices,
    isReady: cameraStatus === MEDIA_PERMISSION_STATUS.GRANTED && microphoneStatus === MEDIA_PERMISSION_STATUS.GRANTED && !!stream,
  }), [stream, cameraStatus, microphoneStatus, permissionError, devices, requestPermissions, stopMedia, inspectDevices])

  return (
    <MediaProctoringContext.Provider value={value}>
      {children}
    </MediaProctoringContext.Provider>
  )
}

export function useMediaProctoring() {
  const ctx = useContext(MediaProctoringContext)
  if (!ctx) {
    throw new Error('useMediaProctoring must be used within MediaProctoringProvider')
  }
  return ctx
}
