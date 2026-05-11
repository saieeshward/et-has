import hashlib
from typing import Optional
from .init_et import InitET, Path

class Blobber:
    def __init__(self, init: InitET) -> None:
        self.blobs_path = init.blobs_path

    def _blob_path(self, blob_hash: str) -> Path:
        return self.blobs_path / blob_hash[:2] / blob_hash

    def save_blob(self, file_path: Path) -> Optional[str]:
        if not file_path.exists():
            print(f"[Blobber] File not found: {file_path}")
            return None

        content: bytes = file_path.read_bytes()
        blob_hash: str = hashlib.sha256(content).hexdigest()

        dest = self._blob_path(blob_hash)
        dest.parent.mkdir(parents=True, exist_ok=True)

        if not dest.exists():
            dest.write_bytes(content)
            print(f"[Blobber] Stored new blob: {blob_hash[:12]}...")
        else:
            print(f"[Blobber] Blob already exists: {blob_hash[:12]}...")

        return blob_hash

    def load_blob(self, blob_hash: str) -> Optional[bytes]:
        path = self._blob_path(blob_hash)
        if not path.exists():
            print(f"[Blobber] Blob not found: {blob_hash}")
            return None
        return path.read_bytes()
