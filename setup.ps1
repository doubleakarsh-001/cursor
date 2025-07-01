# Step 1: Create virtual environment if it doesn't exist
if (!(Test-Path -Path ".\venv")) {
    Write-Output "Creating virtual environment..."
    py -m venv venv
}

# Step 2: Temporarily allow script execution for this session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Step 3: Activate the virtual environment
Write-Output "Activating virtual environment..."
. .\venv\Scripts\Activate.ps1

# Step 4: Install required packages
if (Test-Path -Path "requirements.txt") {
    Write-Output "Installing packages from requirements.txt..."
    py -m pip install -r requirements.txt
} else {
    Write-Output "No requirements.txt found. Skipping package installation."
}

