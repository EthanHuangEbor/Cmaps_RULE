$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Pkg = Join-Path $Root "submission_source"
if (Test-Path $Pkg) { Remove-Item -Recurse -Force $Pkg }
New-Item -ItemType Directory -Force -Path $Pkg | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Pkg "figures") | Out-Null
foreach ($name in @("main.tex", "supplement.tex", "references.bib", "figure_table_manifest.md", "citation_audit.md", "statistical_audit.md", "paper2_value_trace.csv")) {
  Copy-Item -Force (Join-Path $Root $name) $Pkg
}
Copy-Item -Force (Join-Path $Root "figures\*.pdf") (Join-Path $Pkg "figures")
$Zip = Join-Path $Root "paper2_submission_source.zip"
if (Test-Path $Zip) { Remove-Item -Force $Zip }
Compress-Archive -Path (Join-Path $Pkg "*") -DestinationPath $Zip
Write-Host "Created $Zip"
