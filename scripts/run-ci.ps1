# Run full CI workflow
Write-Host "Starting CI Workflow..."

.\scripts\install-deps.ps1
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "Linting..."
ruff check .
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "Type Checking..."
mypy src/lattice_lock
if ($LASTEXITCODE -ne 0) { exit 1 }

.\scripts\run-tests.ps1
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "CI Passed!"
