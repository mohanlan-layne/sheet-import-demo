"""Upload controller for handling sheet import uploads."""
from __future__ import annotations

from pathlib import Path
import tempfile
import uuid

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status

router = APIRouter(prefix="/uploads", tags=["uploads"])

SUPPORTED_TYPES = {
    "text/csv": ".csv",
    "application/vnd.ms-excel": ".xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MiB
_TEMP_ROOT = Path(tempfile.gettempdir()) / "sheet-import-demo"
_TEMP_ROOT.mkdir(parents=True, exist_ok=True)


def _validate_headers(
    content_type: str = Header(..., alias="Content-Type"),
    upload_token: str = Header(..., alias="X-Upload-Token"),
) -> None:
    """Ensure request headers are present and valid."""
    if not content_type.lower().startswith("multipart/form-data"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Content-Type must be multipart/form-data.",
        )
    if not upload_token.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Upload-Token header must not be empty.",
        )


def _validate_file_metadata(upload: UploadFile) -> Path:
    """Validate file metadata and return the destination path."""
    if not upload.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must include a filename.",
        )

    normalized_suffix = Path(upload.filename).suffix.lower()
    expected_suffix = SUPPORTED_TYPES.get(upload.content_type)

    if normalized_suffix not in SUPPORTED_TYPES.values():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File extension is not supported.",
        )

    if expected_suffix is None or expected_suffix != normalized_suffix:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MIME type does not match the provided file extension.",
        )

    file_id = uuid.uuid4().hex
    destination = _TEMP_ROOT / f"{file_id}{normalized_suffix}"
    return destination


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_sheet(
    file: UploadFile = File(...),
    _: None = Depends(_validate_headers),
):
    """Handle sheet uploads and persist them to a temporary location."""
    destination_path = _validate_file_metadata(file)

    total_bytes = 0
    try:
        with destination_path.open("wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > MAX_FILE_SIZE_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Uploaded file exceeds the maximum allowed size.",
                    )
                buffer.write(chunk)
    except HTTPException:
        if destination_path.exists():
            destination_path.unlink(missing_ok=True)
        raise
    finally:
        await file.close()

    return {
        "fileId": destination_path.stem,
        "filename": file.filename,
        "contentType": file.content_type,
        "size": total_bytes,
        "temporaryPath": str(destination_path),
    }
