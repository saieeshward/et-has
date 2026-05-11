import difflib
from typing import Optional
from .commiter import Commiter


class Differ:
    def __init__(self, commiter: Commiter) -> None:
        self.commiter = commiter

    def diff(
        self,
        file_name: str,
        from_commit_id: Optional[str] = None,
        to_commit_id: Optional[str] = None,
    ) -> Optional[str]:
        """Compare a file between two commits. Defaults to HEAD~1 vs HEAD."""
        history = self.commiter.get_history()
        commit_map = {c["commit_id"]: c for c in history}

        if from_commit_id is None:
            if len(history) < 2:
                print("[Differ] Need at least 2 commits to generate default diff.")
                return None
            from_commit = history[1]
        else:
            from_commit = commit_map.get(from_commit_id)
            if from_commit is None:
                print(f"[Differ] Commit not found: {from_commit_id}")
                return None

        if to_commit_id is None:
            if len(history) < 1:
                print("[Differ] No commits in history.")
                return None
            to_commit = history[0]
        else:
            to_commit = commit_map.get(to_commit_id)
            if to_commit is None:
                print(f"[Differ] Commit not found: {to_commit_id}")
                return None

        from_blob_hash = from_commit["files"].get(file_name)
        to_blob_hash = to_commit["files"].get(file_name)

        if from_blob_hash is None:
            print(
                f"[Differ] File '{file_name}' not found in commit {from_commit['commit_id']}"
            )
            return None

        if to_blob_hash is None:
            print(
                f"[Differ] File '{file_name}' not found in commit {to_commit['commit_id']}"
            )
            return None

        from_content = self.commiter.blobber.load_blob(from_blob_hash)
        to_content = self.commiter.blobber.load_blob(to_blob_hash)

        if from_content is None or to_content is None:
            print("[Differ] Failed to load blob content.")
            return None

        try:
            from_text = from_content.decode("utf-8")
            to_text = to_content.decode("utf-8")
        except UnicodeDecodeError:
            print(
                f"[Differ] File '{file_name}' is binary or not UTF-8 decodable. "
                "Cannot generate text diff."
            )
            return None

        from_lines = from_text.splitlines(keepends=True)
        to_lines = to_text.splitlines(keepends=True)

        diff_lines = difflib.unified_diff(
            from_lines,
            to_lines,
            fromfile=f"{file_name} ({from_commit['commit_id']})",
            tofile=f"{file_name} ({to_commit['commit_id']})",
            lineterm="",
        )

        diff_str = "\n".join(diff_lines)

        if diff_str:
            print(
                f"[Differ] Generated diff for '{file_name}' between "
                f"{from_commit['commit_id']} and {to_commit['commit_id']}"
            )
        else:
            print(
                f"[Differ] No differences found for '{file_name}' between commits."
            )

        return diff_str

    def diff_blobs(
        self,
        blob_hash_1: str,
        blob_hash_2: str,
    ) -> Optional[str]:
        """Compare two blobs by their hash values."""
        content_1 = self.commiter.blobber.load_blob(blob_hash_1)
        content_2 = self.commiter.blobber.load_blob(blob_hash_2)

        if content_1 is None:
            print(f"[Differ] Blob not found: {blob_hash_1}")
            return None

        if content_2 is None:
            print(f"[Differ] Blob not found: {blob_hash_2}")
            return None

        try:
            text_1 = content_1.decode("utf-8")
            text_2 = content_2.decode("utf-8")
        except UnicodeDecodeError:
            print("[Differ] One or both blobs are binary or not UTF-8 decodable.")
            return None

        from_lines = text_1.splitlines(keepends=True)
        to_lines = text_2.splitlines(keepends=True)

        diff_lines = difflib.unified_diff(
            from_lines,
            to_lines,
            fromfile=blob_hash_1[:12],
            tofile=blob_hash_2[:12],
            lineterm="",
        )

        return "\n".join(diff_lines)
