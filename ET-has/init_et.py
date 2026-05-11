from pathlib import Path
import os
from typing import Optional

STORE_DIR = ".snapshot"
COMMITS_LOG = "commits.jsonl"
BLOBS_DIR = "blobs"
HEAD_FILE = "HEAD"


class InitET:
    def __init__(self, dir: Optional[str] = None) -> None:
        self.base_dir: Path = Path(dir) if dir else Path(os.getcwd())
        self.store_dir: Path = self.base_dir / STORE_DIR
        self.commits_path: Path = self.store_dir / COMMITS_LOG
        self.blobs_path: Path = self.store_dir / BLOBS_DIR
        self.head_path: Path = self.store_dir / HEAD_FILE
        self._init_store()

    def _init_store(self) -> None:
        if self.store_dir.exists():
            print(f"[InitET] Store already exists at {self.store_dir}")
        else:
            self.store_dir.mkdir(parents=True)
            self.blobs_path.mkdir()
            print(f"[InitET] Initialised new store at {self.store_dir}")
