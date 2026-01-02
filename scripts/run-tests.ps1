# Run tests for Lattice Lock
param (
    [string]$Target = "tests/"
)

Write-Host "Running tests on target: $Target"
pytest $Target -v
if ($LASTEXITCODE -ne 0) {
    Write-Error "Tests failed!"
    exit 1
}
