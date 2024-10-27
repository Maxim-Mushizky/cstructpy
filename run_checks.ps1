# Define paths
$venvPath = ".\venv\Scripts\Activate.ps1"  # Path to the virtual environment activation script
$srcDir = ".\src"                          # Path to the src directory
$testsDir = ".\unit_tests"                 # Path to the unit_tests directory

# Activate the virtual environment
if (Test-Path $venvPath) {
    & $venvPath
    Write-Output "Virtual environment activated."
} else {
    Write-Output "Virtual environment not found at $venvPath"
    exit
}

# Run mypy on src directory
Write-Output "Running mypy on $srcDir..."
mypy $srcDir

# Run flake8 on src directory
Write-Output "Running flake8 on $srcDir..."
flake8 $srcDir

# Run pytest on unit_tests directory
Write-Output "Running pytest on $testsDir..."
pytest $testsDir
