from pathlib import Path
from typing import Optional
from ET_has import InitET, Blobber, Commiter, Differ

init = InitET()
blobber = Blobber(init)
commiter = Commiter(init, blobber)

commiter.make_commit(
    tracked_files=[Path("config.yaml")],
    author="app",
    message="autosave"
)
last_commit: Optional[dict] = commiter.check_last_commit("config.yaml")
if last_commit:
    blob_id = last_commit["files"]["config.yaml"]
    print(blob_id)
    file_content: Optional[bytes] = blobber.load_blob(blob_hash=blob_id)
    print(file_content if file_content else "Nothing")

# Demonstrate Differ functionality
differ = Differ(commiter)
diff = differ.diff("config.yaml")
if diff:
    print("\nDiff output:")
    print(diff)
