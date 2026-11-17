import io
from pathlib import Path
from uuid import uuid4
from typing import Tuple

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": (b"\xff\xd8\xff", ".jpg"),
    "image/png": (b"\x89PNG\r\n\x1a\n", ".png"),
}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


class IdentityImageStorageError(ValueError):
    pass


def get_storage_root() -> Path:
    # backend/app/modules/students -> backend
    backend_root = Path(__file__).resolve().parents[3]
    root = backend_root / "storage" / "identity_verifications"
    root.mkdir(parents=True, exist_ok=True)
    return root


def detect_image_type(content: bytes) -> Tuple[str, str]:
    for mime, (signature, ext) in ALLOWED_IMAGE_TYPES.items():
        if content.startswith(signature):
            return mime, ext
    raise IdentityImageStorageError("Unsupported or invalid image format. Only JPEG and PNG are allowed.")


def _safe_delete_file(path: Path) -> None:
    try:
        if path.exists() and path.is_file():
            path.unlink()
    except OSError:
        # Best-effort cleanup; do not mask original errors.
        pass


def delete_identity_image(relative_path: str | None) -> None:
    if not relative_path:
        return
    try:
        path = resolve_identity_image_path(relative_path)
    except IdentityImageStorageError:
        return
    _safe_delete_file(path)


def validate_image_content(content: bytes, claimed_content_type: str | None, filename: str | None) -> Tuple[str, str]:
    if not content:
        raise IdentityImageStorageError("Image file is empty.")
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise IdentityImageStorageError("Image file exceeds the maximum allowed size of 5 MB.")

    actual_mime, ext = detect_image_type(content)

    if claimed_content_type:
        claimed = claimed_content_type.split(";")[0].strip().lower()
        if claimed not in ALLOWED_IMAGE_TYPES:
            raise IdentityImageStorageError("Unsupported image MIME type.")
        if claimed != actual_mime:
            raise IdentityImageStorageError("Image content does not match the provided file type.")

    if filename:
        lower = filename.lower().strip()
        if "." not in lower:
            raise IdentityImageStorageError("Image file must include a supported extension (.jpg, .jpeg, .png).")
        file_ext = "." + lower.rsplit(".", 1)[-1]
        allowed_exts = {".jpg", ".jpeg", ".png"}
        if file_ext not in allowed_exts:
            raise IdentityImageStorageError("Unsupported image file extension.")
        if actual_mime == "image/jpeg" and file_ext not in {".jpg", ".jpeg"}:
            raise IdentityImageStorageError("File extension does not match image content.")
        if actual_mime == "image/png" and file_ext != ".png":
            raise IdentityImageStorageError("File extension does not match image content.")

    # Structural validation: require decodable, well-formed image content.
    try:
        from PIL import Image  # type: ignore

        img = Image.open(io.BytesIO(content))
        img.verify()
        img2 = Image.open(io.BytesIO(content))
        img2.load()
        fmt = (img2.format or "").upper()
        if actual_mime == "image/jpeg" and fmt != "JPEG":
            raise IdentityImageStorageError("Malformed JPEG image.")
        if actual_mime == "image/png" and fmt != "PNG":
            raise IdentityImageStorageError("Malformed PNG image.")
    except IdentityImageStorageError:
        raise
    except ImportError:
        # Pillow not installed: enforce strict signature/terminator checks.
        if actual_mime == "image/jpeg" and not content.endswith(b"\xff\xd9"):
            raise IdentityImageStorageError("Malformed JPEG image.")
        if actual_mime == "image/png" and not content.endswith(b"\x00\x00\x00\x00IEND\xaeB`\x82"):
            raise IdentityImageStorageError("Malformed PNG image.")
    except Exception:
        if actual_mime == "image/jpeg":
            raise IdentityImageStorageError("Malformed JPEG image.")
        raise IdentityImageStorageError("Malformed PNG image.")

    # Final sanity checks even when Pillow is available.
    if actual_mime == "image/jpeg" and not content.endswith(b"\xff\xd9"):
        raise IdentityImageStorageError("Malformed JPEG image.")
    if actual_mime == "image/png" and not content.endswith(b"\x00\x00\x00\x00IEND\xaeB`\x82"):
        raise IdentityImageStorageError("Malformed PNG image.")

    return actual_mime, ext


def save_identity_image(content: bytes, attempt_id: int, student_id: int, content_type: str, ext: str) -> tuple[str, Path]:
    root = get_storage_root()
    attempt_dir = root / f"attempt_{attempt_id}"
    attempt_dir.mkdir(parents=True, exist_ok=True)
    filename = f"student_{student_id}_{uuid4().hex}{ext}"
    path = attempt_dir / filename
    path.write_bytes(content)
    # return path relative to storage root (no absolute/internal path leakage to API)
    return str(path.relative_to(root)).replace("\\", "/"), path


def resolve_identity_image_path(relative_path: str) -> Path:
    root = get_storage_root().resolve()
    candidate = (root / relative_path).resolve()
    if root not in candidate.parents and candidate != root:
        raise IdentityImageStorageError("Invalid image path.")
    if not candidate.exists() or not candidate.is_file():
        raise IdentityImageStorageError("Identity image not found.")
    return candidate