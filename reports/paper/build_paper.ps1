$ErrorActionPreference = "Stop"

$PaperDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not (Get-Command latexmk -ErrorAction SilentlyContinue)) {
  throw "latexmk was not found on PATH. Install a TeX distribution, then rerun this script."
}

if (-not $env:WINDIR -and $env:SystemRoot) {
  $env:WINDIR = $env:SystemRoot
}

Push-Location $PaperDir
try {
  latexmk -pdf -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
} finally {
  Pop-Location
}

Write-Host "Built reports/paper/build/main.pdf with latexmk."
