"""Cria um ZIP de entrega sem arquivos temporarios ou binarios locais."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "output" / "entrega_n_rainhas.zip"
INCLUDE = [ROOT / "README.md", ROOT / ".gitignore", ROOT / ".gitattributes"]
for folder in ("src", "scripts", "tests", "data", "output/figures", "output/pdf", "output/presentation"):
    INCLUDE.extend(
        path for path in (ROOT / folder).rglob("*")
        if path.is_file()
        and (folder != "output/pdf" or path.suffix.lower() == ".pdf")
        and (folder != "output/presentation" or path.suffix.lower() in {".pdf", ".pptx", ".md"})
    )

DEST.parent.mkdir(parents=True, exist_ok=True)
with ZipFile(DEST, "w", ZIP_DEFLATED) as archive:
    for path in sorted(INCLUDE):
        if path == DEST or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        archive.write(path, path.relative_to(ROOT))
print(f"Pacote: {DEST}")
