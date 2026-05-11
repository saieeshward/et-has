from datetime import datetime, timezone
import uuid
from .blobber import Blobber, InitET, Optional, Path
import json

class Commiter:
    def __init__(self, init: InitET, blobber: Blobber) -> None:
        self.init = init
        self.blobber = blobber
        self.commits_path = init.commits_path
        self.head_path = init.head_path

    def load_jsonl_commits(self) -> list[dict]:
        if not self.commits_path.exists():
            return []
        commits = []
        with self.commits_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    commits.append(json.loads(line))
        return commits

    def _read_head(self) -> Optional[str]:
        if not self.head_path.exists():
            return None
        text = self.head_path.read_text(encoding="utf-8").strip()
        return text or None

    def _write_head(self, commit_id: str) -> None:
        self.head_path.write_text(commit_id, encoding="utf-8")

    def _get_last_commit(self) -> Optional[dict]:
        head = self._read_head()
        if head is None:
            return None
        for commit in reversed(self.load_jsonl_commits()):
            if commit["commit_id"] == head:
                return commit
        return None

    def check_last_commit(self, file_name: str) -> Optional[dict]:
        """Return the last commit entry that includes file_name, or None."""
        last = self._get_last_commit()
        if last and file_name in last.get("files", {}):
            return last
        return None

    def make_commit(
        self,
        tracked_files: list[Path],
        author: Optional[str] = None,
        message: Optional[str] = None,
    ) -> Optional[dict]:
        last_commit = self._get_last_commit()
        last_files: dict = last_commit["files"] if last_commit else {}

        new_files: dict = {}
        changed = False

        for file_path in tracked_files:
            blob_hash = self.blobber.save_blob(file_path)
            if blob_hash is None:
                continue

            # Use relative path string as key
            key = str(file_path)
            new_files[key] = blob_hash

            if last_files.get(key) != blob_hash:
                changed = True

        if not changed and last_commit is not None:
            print("[Commiter] No changes detected. Nothing to commit.")
            return None

        commit_id = str(uuid.uuid4())[:8]
        commit = {
            "commit_id": commit_id,
            "parent": last_commit["commit_id"] if last_commit else None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "author": author or "unknown",
            "message": message or "no message",
            "files": new_files,
        }

        with self.commits_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(commit) + "\n")

        self._write_head(commit_id)
        print(f"[Commiter] Committed: {commit_id}")
        return commit

    def get_history(self) -> list[dict]:
        """Walk parent chain from HEAD and return history newest-first."""
        head = self._read_head()
        if head is None:
            return []

        commit_map = {c["commit_id"]: c for c in self.load_jsonl_commits()}
        history = []
        current = head

        while current is not None:
            commit = commit_map.get(current)
            if commit is None:
                break
            history.append(commit)
            current = commit.get("parent")

        return history

    def restore_file(self, file_name: str, commit_id: str, target_path: Path) -> bool:
        """Restore a specific file from a given commit to target_path."""
        commits = {c["commit_id"]: c for c in self.load_jsonl_commits()}
        commit = commits.get(commit_id)
        if commit is None:
            print(f"[Commiter] Commit {commit_id} not found.")
            return False

        blob_hash = commit["files"].get(file_name)
        if blob_hash is None:
            print(f"[Commiter] File {file_name} not in commit {commit_id}.")
            return False

        content = self.blobber.load_blob(blob_hash)
        if content is None:
            return False

        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(content)
        print(f"[Commiter] Restored {file_name} -> {target_path}")
        return True
