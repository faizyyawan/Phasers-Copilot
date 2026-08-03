Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Fail($Message) {
    Write-Error $Message
    exit 1
}

if ($env:OS -ne "Windows_NT") {
    Fail "This setup script must be run on native Windows PowerShell."
}

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

Write-Host "Project root: $ProjectRoot"
Write-Host "Checking Python 3.11..."
py -3.11 --version
py -3.11 -c "import platform, sys; assert platform.architecture()[0] == '64bit', 'Python 3.11 must be 64-bit'; print(sys.executable); print(platform.architecture())"

Write-Host "Checking NVIDIA GPU..."
$HasNvidiaGpu = $null -ne (Get-Command nvidia-smi -ErrorAction SilentlyContinue)
if ($HasNvidiaGpu) {
    nvidia-smi
} else {
    Write-Warning "nvidia-smi was not found. CPU-only PyTorch will be installed."
}

if (-not (Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
    Write-Host "Creating .venv with Python 3.11..."
    py -3.11 -m venv .venv
} else {
    Write-Host ".venv already exists; reusing it."
}

. .\.venv\Scripts\Activate.ps1

$VenvPython = (Resolve-Path ".venv\Scripts\python.exe").Path
if ((Get-Command python).Source -ne $VenvPython) {
    Fail "Active python is not the project .venv interpreter."
}

python --version
python -m pip install --upgrade pip setuptools wheel

if ($HasNvidiaGpu) {
    Write-Host "Installing CUDA-enabled PyTorch..."
    python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
} else {
    Write-Host "Installing CPU-only PyTorch..."
    python -m pip install torch torchvision torchaudio
}

Write-Host "Installing runtime dependencies..."
python -m pip install -r requirements.txt

Write-Host "Installing development dependencies..."
python -m pip install -r requirements-dev.txt

Write-Host "Running environment verification..."
python .\scripts\verify_environment.py

Write-Host "Setup complete."
