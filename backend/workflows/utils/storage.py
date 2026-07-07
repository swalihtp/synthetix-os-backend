import logging
import os
import shutil
from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile

from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


@contextmanager
def temporary_storage_file(file_path: str):
    """
    Copy a storage-backed file to a local temp file for libraries that need a path.
    Works with both FileSystemStorage and S3-backed storage.
    """
    if not file_path:
        raise ValueError("file_path is required")

    storage_key = str(file_path)
    exists = default_storage.exists(storage_key)
    logger.info(
        "[storage] file_path received=%s exists=%s", storage_key, exists
    )

    if not exists:
        raise FileNotFoundError(
            f"File '{storage_key}' was not found in default_storage"
        )

    temp_path = None
    suffix = Path(storage_key).suffix

    try:
        with default_storage.open(storage_key, "rb") as source:
            with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                shutil.copyfileobj(source, temp_file)
                temp_path = temp_file.name

        logger.info("[storage] temp file created=%s for file_path=%s", temp_path, storage_key)
        yield temp_path
        logger.info("[storage] extraction completed for file_path=%s", storage_key)
    except Exception:
        logger.exception("[storage] failed while staging file_path=%s", storage_key)
        raise
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                logger.info("[storage] temp file removed=%s", temp_path)
            except OSError:
                logger.exception("[storage] failed to remove temp file=%s", temp_path)
