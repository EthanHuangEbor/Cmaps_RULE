from __future__ import annotations

from pathlib import Path
import zipfile

from scripts.package_arxiv_source import build_package


def test_build_package_removes_stale_files_and_writes_zip(tmp_path: Path) -> None:
    paper = tmp_path / "reports" / "paper"
    (paper / "figures").mkdir(parents=True)
    (paper / "build").mkdir()
    (paper / "main.tex").write_text(
        r"\includegraphics[width=\textwidth]{figure_09_metric_rank_heatmap.pdf}" "\n",
        encoding="utf-8",
    )
    (paper / "references.bib").write_text("@misc{demo}\n", encoding="utf-8")
    (paper / "build" / "main.bbl").write_text("\\begin{thebibliography}{}\n", encoding="utf-8")
    (paper / "figures" / "figure_09_metric_rank_heatmap.pdf").write_bytes(b"%PDF-1.4\n")

    out_dir = paper / "arxiv_upload"
    stale = out_dir / "figures" / "old_figure.pdf"
    stale.parent.mkdir(parents=True)
    stale.write_bytes(b"old")

    zip_path = paper / "arxiv_upload.zip"
    build_package(tmp_path, out_dir, zip_path=zip_path)

    assert not stale.exists()
    assert (out_dir / "main.tex").exists()
    assert (out_dir / "figures" / "figure_09_metric_rank_heatmap.pdf").exists()
    assert zip_path.exists()
    with zipfile.ZipFile(zip_path) as archive:
        assert sorted(archive.namelist()) == [
            "figures/figure_09_metric_rank_heatmap.pdf",
            "main.bbl",
            "main.tex",
            "references.bib",
            "source_manifest.txt",
        ]
