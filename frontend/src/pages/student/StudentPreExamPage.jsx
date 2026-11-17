import { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import AppLayout from '../../components/layout/AppLayout'
import Badge from '../../components/shared/Badge'
import Button from '../../components/shared/Button'
import Card from '../../components/shared/Card'
import Spinner from '../../components/shared/Spinner'
import { useToast } from '../../components/shared/Toast'
import { studentService } from '../../services/studentService'
import { ROUTES } from '../../utils/constants'
import { MEDIA_PERMISSION_STATUS, useMediaProctoring } from '../../context/MediaProctoringContext'

const IDENTITY_STATUS = {
  NOT_SUBMITTED: 'not_submitted',
  PENDING: 'pending',
  VERIFIED: 'verified',
  REJECTED: 'rejected',
}

function mediaStatusLabel(status) {
  switch (status) {
    case MEDIA_PERMISSION_STATUS.IDLE:
      return 'Not requested'
    case MEDIA_PERMISSION_STATUS.REQUESTING:
      return 'Requesting'
    case MEDIA_PERMISSION_STATUS.GRANTED:
      return 'Granted'
    case MEDIA_PERMISSION_STATUS.DENIED:
      return 'Denied'
    case MEDIA_PERMISSION_STATUS.UNAVAILABLE:
      return 'Unavailable'
    case MEDIA_PERMISSION_STATUS.ERROR:
      return 'Error'
    default:
      return 'Unknown'
  }
}

function mediaStatusVariant(status) {
  if (status === MEDIA_PERMISSION_STATUS.GRANTED) return 'primary'
  if (status === MEDIA_PERMISSION_STATUS.REQUESTING) return 'warning'
  if (status === MEDIA_PERMISSION_STATUS.IDLE) return 'default'
  return 'danger'
}

function identityStatusLabel(status, uploading) {
  if (uploading) return 'Uploading'
  switch (status) {
    case IDENTITY_STATUS.NOT_SUBMITTED:
      return 'Not submitted'
    case IDENTITY_STATUS.PENDING:
      return 'Pending review'
    case IDENTITY_STATUS.VERIFIED:
      return 'Verified'
    case IDENTITY_STATUS.REJECTED:
      return 'Rejected'
    default:
      return 'Not submitted'
  }
}

function identityStatusVariant(status, uploading, uploadFailed) {
  if (uploading) return 'warning'
  if (uploadFailed) return 'danger'
  switch (status) {
    case IDENTITY_STATUS.PENDING:
      return 'warning'
    case IDENTITY_STATUS.VERIFIED:
      return 'primary'
    case IDENTITY_STATUS.REJECTED:
      return 'danger'
    default:
      return 'default'
  }
}

function LiveCameraPreview({ stream }) {
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

  return (
    <div className="w-full aspect-video bg-[var(--color-surface-soft)] border border-[var(--color-border)] rounded-lg overflow-hidden flex items-center justify-center">
      {stream ? (
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="w-full h-full object-cover"
          aria-label="Live camera preview for identity verification"
        />
      ) : (
        <p className="text-sm text-[var(--color-text-muted)] px-4 text-center">
          Camera preview will appear here after camera and microphone access is granted.
        </p>
      )}
    </div>
  )
}

export default function StudentPreExamPage() {
  const { attemptId } = useParams()
  const navigate = useNavigate()
  const toast = useToast()
  const captureVideoRef = useRef(null)
  const canvasRef = useRef(null)

  const [starting, setStarting] = useState(false)
  const [error, setError] = useState('')

  const [identityStatus, setIdentityStatus] = useState(IDENTITY_STATUS.NOT_SUBMITTED)
  const [identityLoading, setIdentityLoading] = useState(true)
  const [identityUploading, setIdentityUploading] = useState(false)
  const [identityUploadFailed, setIdentityUploadFailed] = useState(false)
  const [identityMessage, setIdentityMessage] = useState('')
  const [capturedPhotoUrl, setCapturedPhotoUrl] = useState(null)
  const [capturedPhotoBlob, setCapturedPhotoBlob] = useState(null)
  const [captureError, setCaptureError] = useState('')

  const {
    stream,
    cameraStatus,
    microphoneStatus,
    permissionError,
    requestPermissions,
    isReady,
  } = useMediaProctoring()

  const identitySubmitted = identityStatus === IDENTITY_STATUS.PENDING || identityStatus === IDENTITY_STATUS.VERIFIED
  const canStart = isReady && identitySubmitted && !identityUploading

  useEffect(() => {
    let active = true
    const loadIdentityStatus = async () => {
      setIdentityLoading(true)
      try {
        const data = await studentService.getIdentityVerificationStatus(attemptId)
        if (!active) return
        setIdentityStatus(data.status || IDENTITY_STATUS.NOT_SUBMITTED)
        setIdentityMessage(data.message || '')
        setIdentityUploadFailed(false)
      } catch (err) {
        if (!active) return
        // If status cannot be loaded, keep conservative not-submitted state and show error.
        setIdentityMessage(err.message || 'Could not load identity verification status.')
      } finally {
        if (active) setIdentityLoading(false)
      }
    }
    loadIdentityStatus()
    return () => {
      active = false
    }
  }, [attemptId])

  useEffect(() => {
    const video = captureVideoRef.current
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

  useEffect(() => {
    return () => {
      if (capturedPhotoUrl) {
        URL.revokeObjectURL(capturedPhotoUrl)
      }
    }
  }, [capturedPhotoUrl])

  const handleBack = () => {
    navigate(ROUTES.STUDENT_DASHBOARD)
  }

  const handleRequestPermissions = async () => {
    setError('')
    await requestPermissions()
  }

  const handleCapturePhoto = async () => {
    setCaptureError('')
    if (!stream || cameraStatus !== MEDIA_PERMISSION_STATUS.GRANTED) {
      setCaptureError('Camera access is required before capturing your identity photo.')
      return
    }
    const video = captureVideoRef.current
    if (!video || !video.videoWidth || !video.videoHeight) {
      setCaptureError('Camera is not ready yet. Please wait for the live preview and try again.')
      return
    }
    try {
      const canvas = canvasRef.current || document.createElement('canvas')
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      const ctx = canvas.getContext('2d')
      if (!ctx) {
        setCaptureError('Could not capture photo in this browser.')
        return
      }
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
      const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.92))
      if (!blob) {
        setCaptureError('Could not create the photo. Please try again.')
        return
      }
      if (capturedPhotoUrl) URL.revokeObjectURL(capturedPhotoUrl)
      const url = URL.createObjectURL(blob)
      setCapturedPhotoBlob(blob)
      setCapturedPhotoUrl(url)
      setIdentityUploadFailed(false)
    } catch {
      setCaptureError('Photo capture failed. Please try again.')
    }
  }

  const handleRetakePhoto = () => {
    setCaptureError('')
    setIdentityUploadFailed(false)
    if (capturedPhotoUrl) URL.revokeObjectURL(capturedPhotoUrl)
    setCapturedPhotoUrl(null)
    setCapturedPhotoBlob(null)
  }

  const handleSubmitIdentityPhoto = async () => {
    if (!capturedPhotoBlob) {
      setCaptureError('Please capture a photo before submitting.')
      return
    }
    if (identitySubmitted) {
      return
    }
    setIdentityUploading(true)
    setIdentityUploadFailed(false)
    setCaptureError('')
    setError('')
    try {
      const result = await studentService.submitIdentityVerification(attemptId, capturedPhotoBlob)
      setIdentityStatus(result.status || IDENTITY_STATUS.PENDING)
      setIdentityMessage(result.message || 'Identity photo submitted and pending manual review.')
      setIdentityUploadFailed(false)
      // Clear captured preview after successful submit to prevent duplicate submissions.
      if (capturedPhotoUrl) URL.revokeObjectURL(capturedPhotoUrl)
      setCapturedPhotoUrl(null)
      setCapturedPhotoBlob(null)
      toast.success('Identity photo submitted for manual review')
    } catch (err) {
      setIdentityUploadFailed(true)
      setCaptureError(err.message || 'Upload failed. Please try again.')
    } finally {
      setIdentityUploading(false)
    }
  }

  const handleStartExamination = async () => {
    if (!isReady) {
      setError('Camera and microphone access are required before starting the examination.')
      return
    }
    if (!identitySubmitted) {
      setError('You must submit your identity photo before starting the examination.')
      return
    }
    setError('')
    setStarting(true)
    try {
      // Re-check status before start to recover from refresh/state issues.
      const statusData = await studentService.getIdentityVerificationStatus(attemptId)
      setIdentityStatus(statusData.status || IDENTITY_STATUS.NOT_SUBMITTED)
      if (!(statusData.status === IDENTITY_STATUS.PENDING || statusData.status === IDENTITY_STATUS.VERIFIED)) {
        setError(statusData.message || 'Identity verification is required before starting the examination.')
        return
      }
      const startedAttempt = await studentService.startAttempt(attemptId)
      toast.success('Examination started')
      navigate(ROUTES.STUDENT_EXAM.replace(':attemptId', String(attemptId)), {
        state: {
          timeLimitEndsAt: startedAttempt.time_limit_ends_at,
        },
      })
    } catch (err) {
      setError(err.message || 'Could not start the examination. Please try again.')
    } finally {
      setStarting(false)
    }
  }

  const requesting =
    cameraStatus === MEDIA_PERMISSION_STATUS.REQUESTING ||
    microphoneStatus === MEDIA_PERMISSION_STATUS.REQUESTING
  const showRetry =
    [MEDIA_PERMISSION_STATUS.DENIED, MEDIA_PERMISSION_STATUS.UNAVAILABLE, MEDIA_PERMISSION_STATUS.ERROR].includes(cameraStatus) ||
    [MEDIA_PERMISSION_STATUS.DENIED, MEDIA_PERMISSION_STATUS.UNAVAILABLE, MEDIA_PERMISSION_STATUS.ERROR].includes(microphoneStatus)

  return (
    <AppLayout>
      <div className="space-y-8">
        <div>
          <span className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider">
            Pre-Examination Readiness
          </span>
          <h1 className="page-title mt-1">System Check & Identity Verification</h1>
          <p className="text-[var(--color-text-secondary)] text-sm mt-1">
            Complete camera/microphone setup and submit a one-time identity photo before starting your examination.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-5xl">
          <Card>
            <h2 className="text-base font-bold mb-4 text-[var(--color-text-primary)]">Camera & Microphone Setup</h2>
            <LiveCameraPreview stream={stream} />
            <div className="mt-4 space-y-3">
              <div className="flex items-center justify-between gap-3">
                <span className="text-sm font-medium">Camera</span>
                <Badge variant={mediaStatusVariant(cameraStatus)}>{mediaStatusLabel(cameraStatus)}</Badge>
              </div>
              <div className="flex items-center justify-between gap-3">
                <span className="text-sm font-medium">Microphone</span>
                <Badge variant={mediaStatusVariant(microphoneStatus)}>{mediaStatusLabel(microphoneStatus)}</Badge>
              </div>
            </div>

            <div className="mt-4 space-y-3">
              {cameraStatus === MEDIA_PERMISSION_STATUS.IDLE && microphoneStatus === MEDIA_PERMISSION_STATUS.IDLE && (
                <p className="text-sm text-[var(--color-text-secondary)]">
                  Click &quot;Enable Camera & Microphone&quot; to request access. Access is requested only when you click the button.
                </p>
              )}
              {requesting && (
                <div className="flex items-center gap-2 text-sm text-[var(--color-text-secondary)]">
                  <Spinner size="sm" />
                  <span>Requesting camera and microphone access…</span>
                </div>
              )}
              {permissionError && <p className="text-sm text-[var(--color-danger)]">{permissionError}</p>}
              {(cameraStatus === MEDIA_PERMISSION_STATUS.DENIED || microphoneStatus === MEDIA_PERMISSION_STATUS.DENIED) && (
                <div className="text-sm text-[var(--color-text-secondary)] space-y-1">
                  <p className="font-semibold text-[var(--color-text-primary)]">How to allow access:</p>
                  <p>1. Click the camera/microphone icon in your browser address bar.</p>
                  <p>2. Allow camera and microphone for this site.</p>
                  <p>3. Click &quot;Retry&quot; below.</p>
                </div>
              )}
            </div>

            <div className="mt-4 flex flex-wrap gap-3">
              {cameraStatus === MEDIA_PERMISSION_STATUS.IDLE && microphoneStatus === MEDIA_PERMISSION_STATUS.IDLE && (
                <Button onClick={handleRequestPermissions} disabled={requesting}>
                  Enable Camera & Microphone
                </Button>
              )}
              {showRetry && (
                <Button onClick={handleRequestPermissions} disabled={requesting}>
                  Retry
                </Button>
              )}
              {isReady && <Badge variant="primary">Camera and microphone ready</Badge>}
            </div>
          </Card>

          <Card>
            <h2 className="text-base font-bold mb-2 text-[var(--color-text-primary)]">Identity Verification (One-Time Photo)</h2>
            <div className="text-sm text-[var(--color-text-secondary)] space-y-2 mb-4">
              <p>Capture one clear photo of yourself using your webcam for manual identity review.</p>
              <p>This photo is submitted explicitly by you and reviewed manually by authorized staff.</p>
              <p className="font-medium text-[var(--color-text-primary)]">
                No continuous video or audio recording takes place. No automated face recognition or biometric matching is used.
              </p>
            </div>

            <div className="flex items-center justify-between gap-3 mb-4">
              <span className="text-sm font-medium">Verification status</span>
              <div className="flex items-center gap-2">
                <Badge variant={identityStatusVariant(identityStatus, identityUploading, identityUploadFailed)}>
                  {identityStatusLabel(identityStatus, identityUploading)}
                </Badge>
                {identityLoading && <Spinner size="sm" />}
              </div>
            </div>

            {identityMessage && !identityUploadFailed && (
              <p className="text-sm text-[var(--color-text-secondary)] mb-4">{identityMessage}</p>
            )}
            {identityUploadFailed && (
              <p className="text-sm text-[var(--color-danger)] mb-4">Upload failed. {captureError || 'Please try again.'}</p>
            )}

            {/* Hidden video/canvas used for explicit capture from shared stream */}
            <video ref={captureVideoRef} className="hidden" playsInline muted autoPlay aria-hidden="true" />
            <canvas ref={canvasRef} className="hidden" aria-hidden="true" />

            {!identitySubmitted && (
              <div className="space-y-4">
                {!capturedPhotoUrl ? (
                  <div className="space-y-3">
                    <p className="text-sm text-[var(--color-text-secondary)]">
                      Use the live camera preview on the left and click &quot;Capture Photo&quot; when you are ready.
                    </p>
                    <Button onClick={handleCapturePhoto} disabled={!isReady || requesting || identityUploading}>
                      Capture Photo
                    </Button>
                    {!isReady && (
                      <p className="text-xs text-[var(--color-text-muted)]">
                        Enable camera and microphone first to capture your identity photo.
                      </p>
                    )}
                  </div>
                ) : (
                  <div className="space-y-3">
                    <p className="text-sm font-medium text-[var(--color-text-primary)]">Review your photo</p>
                    <div className="w-full max-w-sm aspect-video bg-[var(--color-surface-soft)] border border-[var(--color-border)] rounded-lg overflow-hidden">
                      <img src={capturedPhotoUrl} alt="Captured identity preview" className="w-full h-full object-cover" />
                    </div>
                    <p className="text-xs text-[var(--color-text-muted)]">
                      Confirm to submit this photo for manual review, or retake it.
                    </p>
                    <div className="flex flex-wrap gap-3">
                      <Button onClick={handleSubmitIdentityPhoto} loading={identityUploading} disabled={identityUploading}>
                        Confirm &amp; Submit
                      </Button>
                      <Button variant="secondary" onClick={handleRetakePhoto} disabled={identityUploading}>
                        Retake
                      </Button>
                    </div>
                  </div>
                )}
                {captureError && !identityUploadFailed && (
                  <p className="text-sm text-[var(--color-danger)]">{captureError}</p>
                )}
              </div>
            )}

            {identitySubmitted && (
              <div className="space-y-2">
                <p className="text-sm text-[var(--color-text-secondary)]">
                  Your identity photo has been submitted. You can proceed to start the examination while it remains pending manual review.
                </p>
              </div>
            )}
          </Card>
        </div>

        <Card className="max-w-5xl bg-[var(--color-surface-soft)] border border-[var(--color-border)]">
          <h2 className="text-base font-bold mb-2 text-[var(--color-text-primary)]">Before you start</h2>
          <ul className="text-sm text-[var(--color-text-secondary)] space-y-1 list-disc list-inside">
            <li>Ensure your face is clearly visible in the camera preview.</li>
            <li>Submit a one-time identity photo for manual review (required).</li>
            <li>Live monitoring during the exam is separate and does not record or upload video/audio/frames.</li>
            <li>The examination timer starts only when you click &quot;Start Examination&quot;.</li>
          </ul>
          <p className="text-xs text-[var(--color-text-muted)] mt-3">Attempt ID: {attemptId}</p>
        </Card>

        {error && (
          <Card className="max-w-5xl">
            <p className="text-sm text-[var(--color-danger)]">{error}</p>
          </Card>
        )}

        <div className="flex gap-3">
          <Button
            size="lg"
            loading={starting}
            onClick={handleStartExamination}
            disabled={starting || !canStart || identityLoading}
          >
            Start Examination →
          </Button>
          <Button variant="secondary" onClick={handleBack} size="lg">
            Back to Dashboard
          </Button>
        </div>
      </div>
    </AppLayout>
  )
}
