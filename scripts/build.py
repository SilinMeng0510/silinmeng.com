"""Package the static site without a framework or third-party dependencies."""

from pathlib import Path
import shutil
from render_site import render


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "out"
PUBLIC_FILES = (
    "index.html",
    "cv.html",
    "dist/css/main.css",
    "dist/css/cv.css",
    "dist/js/cv.js",
    "images/favicon.svg",
    "images/icon.jpeg",
    "images/title.jpg",
)


def main():
    render(ROOT)
    # Check every input before replacing the generated output directory.
    for relative in PUBLIC_FILES:
        if not (ROOT / relative).is_file():
            raise FileNotFoundError(f"Missing public file: {relative}")

    if OUTPUT.is_symlink():
        raise RuntimeError("Refusing to replace a symlink at out/")
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)

    for relative in PUBLIC_FILES:
        destination = OUTPUT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, destination)

    size = sum((OUTPUT / relative).stat().st_size for relative in PUBLIC_FILES)
    print(f"Built {len(PUBLIC_FILES)} public files in out/ ({size:,} bytes).")


if __name__ == "__main__":
    main()
