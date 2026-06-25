from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


INCLUDE_GRAPHICS_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")


def referenced_figures(tex_path: Path) -> list[str]:
    text = tex_path.read_text(encoding="utf-8")
    figures: list[str] = []
    for match in INCLUDE_GRAPHICS_RE.finditer(text):
        name = match.group(1)
        if not name.lower().endswith(".pdf"):
            name = f"{name}.pdf"
        figures.append(name)
    return sorted(set(figures))


def copy_if_exists(src: Path, dst: Path, required: bool = False) -> bool:
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    if required:
        raise FileNotFoundError(f"Required arXiv source file is missing: {src}")
    return False


def build_package(root: Path, out_dir: Path) -> None:
    paper_dir = root / "reports" / "paper"
    figure_dir = paper_dir / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    copy_if_exists(paper_dir / "main.tex", out_dir / "main.tex", required=True)
    copied.append("main.tex")

    if copy_if_exists(paper_dir / "references.bib", out_dir / "references.bib"):
        copied.append("references.bib")

    build_bbl = paper_dir / "build" / "main.bbl"
    if copy_if_exists(build_bbl, out_dir / "main.bbl"):
        copied.append("main.bbl")

    figure_names = referenced_figures(paper_dir / "main.tex")
    missing: list[str] = []
    for figure_name in figure_names:
        src = figure_dir / Path(figure_name).name
        dst = out_dir / "figures" / Path(figure_name).name
        if copy_if_exists(src, dst):
            copied.append(f"figures/{Path(figure_name).name}")
        else:
            missing.append(str(src))

    missing_lines = [f"- {path}" for path in missing] if missing else ["None"]
    manifest_lines = [
        "C-MAPSS RUL arXiv source package",
        "",
        "Included files:",
        *[f"- {path}" for path in copied],
        "",
        "Excluded by design:",
        "- raw NASA C-MAPSS data",
        "- model checkpoints and joblib files",
        "- local LaTeX build intermediates",
        "- reviewer reports and response drafts",
        "- large experiment tables not referenced by LaTeX",
        "",
        "Missing referenced figures:",
        *missing_lines,
    ]
    (out_dir / "source_manifest.txt").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    if missing:
        raise FileNotFoundError("Some referenced figures were not found. See source_manifest.txt.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a clean arXiv source upload directory.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args()

    root = args.root.resolve()
    out_dir = args.out_dir or (root / "reports" / "paper" / "arxiv_upload")
    build_package(root, out_dir)
    print(f"Wrote clean arXiv source package to {out_dir}")


if __name__ == "__main__":
    main()
