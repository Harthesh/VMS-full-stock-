from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from shutil import copyfileobj
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


class AbstractStorageService(ABC):
    @abstractmethod
    def save(self, upload: UploadFile, folder: str) -> tuple[str, str]:
        raise NotImplementedError


class LocalStorageService(AbstractStorageService):
    def __init__(self, root: str) -> None:
        self.root = Path(root)

    def save(self, upload: UploadFile, folder: str) -> tuple[str, str]:
        folder_path = self.root / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        safe_name = f"{uuid4().hex}_{upload.filename or 'document'}"
        destination = folder_path / safe_name
        with destination.open("wb") as file_handle:
            copyfileobj(upload.file, file_handle)
        return safe_name, str(destination.relative_to(self.root))


storage_service = LocalStorageService(settings.storage_root)

