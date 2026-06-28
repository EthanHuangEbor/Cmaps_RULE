$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Source = Join-Path $Root "build\source"
New-Item -ItemType Directory -Force -Path $Source | Out-Null
Copy-Item -Force (Join-Path $Root "main.tex") $Source
Copy-Item -Force (Join-Path $Root "supplement.tex") $Source
Copy-Item -Force (Join-Path $Root "references.bib") $Source
New-Item -ItemType Directory -Force -Path (Join-Path $Source "figures") | Out-Null
Copy-Item -Force (Join-Path $Root "figures\*.pdf") (Join-Path $Source "figures")

foreach ($tool in @("pdflatex", "bibtex")) {
  if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
    throw "$tool was not found on PATH. Install LaTeX, then rerun this script."
  }
}

Push-Location $Source
try {
  pdflatex -interaction=nonstopmode -halt-on-error main.tex
  bibtex main
  pdflatex -interaction=nonstopmode -halt-on-error main.tex
  pdflatex -interaction=nonstopmode -halt-on-error main.tex
  pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
  pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
} finally {
  Pop-Location
}
Copy-Item -Force (Join-Path $Source "main.pdf") (Join-Path $Root "paper2_main.pdf")
Copy-Item -Force (Join-Path $Source "supplement.pdf") (Join-Path $Root "paper2_supplement.pdf")
Write-Host "Built paper2_main.pdf and paper2_supplement.pdf"
