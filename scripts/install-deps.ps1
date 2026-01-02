# Install dependencies for Lattice Lock
Write-Host "Installing dependencies..."
pip install --upgrade pip
pip install -e .[dev,mcp]
if ($LASTEXITCODE -ne 0) {
    Write-Error "Dependency installation failed!"
    exit 1
}
