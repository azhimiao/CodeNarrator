"""Create a self-contained skill zip without source repositories or caches."""
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[1]
source = root / "code-narrator"
destination = root / "dist/code-narrator.zip"
destination.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(source.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
            archive.write(path, path.relative_to(root).as_posix())
    license_file = root / "LICENSE"
    if license_file.is_file():
        archive.write(license_file, "LICENSE")
print(destination)
