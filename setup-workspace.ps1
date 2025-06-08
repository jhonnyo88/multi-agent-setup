# =============================================================================
# DigiNativa AI-Team Workspace Setup Script (PowerShell)
# =============================================================================
#
# PURPOSE:
# Sets up the complete workspace for cross-repository AI development:
# - AI-team repo (multi-agent-setup): This repository
# - Product repo (diginativa-game): Cloned to workspace/
# - Proper directory structure for agents to work in
#
# USAGE:
# 1. Open PowerShell in your multi-agent-setup directory
# 2. Run: .\setup-workspace.ps1
# 3. Follow the prompts
#
# REQUIREMENTS:
# - Git must be installed and accessible from PowerShell
# - GitHub token must be configured in .env file
# - Internet connection for cloning repositories
#
# =============================================================================

Write-Host "🚀 DigiNativa AI-Team Workspace Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path ".git") -or -not (Test-Path "agents")) {
    Write-Host "❌ Error: Please run this script from the multi-agent-setup repository root" -ForegroundColor Red
    Write-Host "   Expected files: .git/, agents/, tools/, etc." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Running from correct directory: $(Get-Location)" -ForegroundColor Green

# =============================================================================
# Step 1: Verify Prerequisites
# =============================================================================

Write-Host "`n📋 Step 1: Verifying Prerequisites..." -ForegroundColor Yellow

# Check Git installation
try {
    $gitVersion = git --version
    Write-Host "✅ Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git not found. Please install Git and try again." -ForegroundColor Red
    Write-Host "   Download from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found" -ForegroundColor Red
    Write-Host "   Please create .env file with your configuration" -ForegroundColor Yellow
    Write-Host "   Copy from .env.template and fill in your values" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ .env file found" -ForegroundColor Green

# Check Python installation (optional but recommended)
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Python not found (optional)" -ForegroundColor Yellow
    Write-Host "   Install Python 3.9+ to run AI agents locally" -ForegroundColor Yellow
}

# =============================================================================
# Step 2: Create Workspace Directory Structure
# =============================================================================

Write-Host "`n🏗️  Step 2: Creating Workspace Structure..." -ForegroundColor Yellow

$workspaceDir = "workspace"
$productRepoName = "diginativa-game"  # 🔧 CHANGE: Update this for your product repo
$productRepoPath = "$workspaceDir/$productRepoName"

# Create workspace directory
if (-not (Test-Path $workspaceDir)) {
    New-Item -ItemType Directory -Path $workspaceDir -Force | Out-Null
    Write-Host "✅ Created workspace directory: $workspaceDir" -ForegroundColor Green
} else {
    Write-Host "✅ Workspace directory exists: $workspaceDir" -ForegroundColor Green
}

# Create additional directories for AI team operations
$additionalDirs = @(
    "state/logs",
    "reports/specs",
    "monitoring/reports"
)

foreach ($dir in $additionalDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✅ Created directory: $dir" -ForegroundColor Green
    }
}

# =============================================================================
# Step 3: Clone or Update Product Repository
# =============================================================================

Write-Host "`n📦 Step 3: Setting up Product Repository..." -ForegroundColor Yellow

# Check if product repo already exists
if (Test-Path $productRepoPath) {
    Write-Host "📂 Product repo already exists at: $productRepoPath" -ForegroundColor Yellow
    
    # Ask if user wants to update
    $updateChoice = Read-Host "Do you want to update it? (y/N)"
    if ($updateChoice -eq "y" -or $updateChoice -eq "Y") {
        Write-Host "🔄 Updating product repository..." -ForegroundColor Yellow
        
        Push-Location $productRepoPath
        try {
            git fetch origin
            git checkout main
            git pull origin main
            Write-Host "✅ Product repository updated successfully" -ForegroundColor Green
        } catch {
            Write-Host "❌ Failed to update repository: $_" -ForegroundColor Red
            Write-Host "   You may need to resolve conflicts manually" -ForegroundColor Yellow
        }
        Pop-Location
    } else {
        Write-Host "⏭️  Skipping repository update" -ForegroundColor Yellow
    }
} else {
    # Clone the product repository
    Write-Host "🔄 Cloning product repository..." -ForegroundColor Yellow
    
    # 🔧 CHANGE: Update these repository details for your project
    $repoOwner = "jhonnyo88"      # Your GitHub username
    $repoName = "diginativa-game" # Your product repository name
    $repoUrl = "https://github.com/$repoOwner/$repoName.git"
    
    Write-Host "   Repository: $repoUrl" -ForegroundColor Cyan
    Write-Host "   Target: $productRepoPath" -ForegroundColor Cyan
    
    try {
        git clone $repoUrl $productRepoPath
        Write-Host "✅ Product repository cloned successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to clone repository: $_" -ForegroundColor Red
        Write-Host "`n🔧 Troubleshooting tips:" -ForegroundColor Yellow
        Write-Host "   1. Check your internet connection" -ForegroundColor White
        Write-Host "   2. Verify the repository URL: $repoUrl" -ForegroundColor White
        Write-Host "   3. Ensure you have access to the repository" -ForegroundColor White
        Write-Host "   4. Check if GitHub token is configured correctly" -ForegroundColor White
        exit 1
    }
}

# =============================================================================
# Step 4: Create Required Directory Structure in Product Repo
# =============================================================================

Write-Host "`n📁 Step 4: Setting up Product Repository Structure..." -ForegroundColor Yellow

# Required directories for AI team workflow
$productDirs = @(
    "docs/specs",           # Speldesigner creates UX specifications here
    "frontend/src/components", # Utvecklare creates React components here
    "backend/app/api",      # Utvecklare creates FastAPI endpoints here
    "tests/integration",    # Testutvecklare creates integration tests here
    "tests/fixtures"        # Test data and fixtures
)

foreach ($dir in $productDirs) {
    $fullPath = "$productRepoPath/$dir"
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "✅ Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "✅ Exists: $dir" -ForegroundColor Green
    }
}

# Create .gitkeep files to ensure empty directories are tracked
$gitkeepDirs = @("docs/specs", "tests/fixtures")
foreach ($dir in $gitkeepDirs) {
    $gitkeepPath = "$productRepoPath/$dir/.gitkeep"
    if (-not (Test-Path $gitkeepPath)) {
        New-Item -ItemType File -Path $gitkeepPath -Force | Out-Null
        Write-Host "✅ Created .gitkeep in: $dir" -ForegroundColor Green
    }
}

# =============================================================================
# Step 5: Install Python Dependencies (if Python is available)
# =============================================================================

Write-Host "`n🐍 Step 5: Python Dependencies..." -ForegroundColor Yellow

try {
    python --version | Out-Null
    
    # Check if virtual environment should be created
    if (-not (Test-Path "venv") -and -not (Test-Path ".venv")) {
        $venvChoice = Read-Host "Create Python virtual environment? (Y/n)"
        if ($venvChoice -ne "n" -and $venvChoice -ne "N") {
            Write-Host "🔄 Creating virtual environment..." -ForegroundColor Yellow
            python -m venv venv
            Write-Host "✅ Virtual environment created: venv/" -ForegroundColor Green
            Write-Host "   Activate with: .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
        }
    }
    
    # Check if requirements should be installed
    if (Test-Path "requirements.txt") {
        $installChoice = Read-Host "Install Python requirements? (Y/n)"
        if ($installChoice -ne "n" -and $installChoice -ne "N") {
            Write-Host "🔄 Installing Python requirements..." -ForegroundColor Yellow
            
            # Activate virtual environment if it exists
            if (Test-Path "venv/Scripts/Activate.ps1") {
                & "venv/Scripts/Activate.ps1"
            }
            
            pip install -r requirements.txt
            Write-Host "✅ Python requirements installed" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "⏭️  Python not available, skipping dependency installation" -ForegroundColor Yellow
}

# =============================================================================
# Step 6: Validate Configuration
# =============================================================================

Write-Host "`n🔍 Step 6: Validating Configuration..." -ForegroundColor Yellow

# Check .env configuration
if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    
    # Check for required environment variables
    $requiredVars = @("ANTHROPIC_API_KEY", "GITHUB_TOKEN")
    foreach ($var in $requiredVars) {
        if ($envContent -match "$var=\[YOUR_.*\]" -or $envContent -notmatch "$var=") {
            Write-Host "⚠️  $var not configured in .env" -ForegroundColor Yellow
        } else {
            Write-Host "✅ $var configured" -ForegroundColor Green
        }
    }
}

# Check Git configuration
try {
    $gitUser = git config user.name
    $gitEmail = git config user.email
    
    if ($gitUser -and $gitEmail) {
        Write-Host "✅ Git user configured: $gitUser <$gitEmail>" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Git user not fully configured" -ForegroundColor Yellow
        Write-Host "   Run: git config --global user.name 'Your Name'" -ForegroundColor Cyan
        Write-Host "   Run: git config --global user.email 'your.email@example.com'" -ForegroundColor Cyan
    }
} catch {
    Write-Host "⚠️  Could not check Git configuration" -ForegroundColor Yellow
}

# =============================================================================
# Step 7: Test Workspace Setup
# =============================================================================

Write-Host "`n🧪 Step 7: Testing Workspace Setup..." -ForegroundColor Yellow

# Test 1: Check directory structure
$testPassed = $true

$criticalPaths = @(
    $workspaceDir,
    $productRepoPath,
    "$productRepoPath/docs/specs",
    "$productRepoPath/frontend/src/components",
    "$productRepoPath/backend/app/api"
)

foreach ($path in $criticalPaths) {
    if (Test-Path $path) {
        Write-Host "✅ Path exists: $path" -ForegroundColor Green
    } else {
        Write-Host "❌ Missing path: $path" -ForegroundColor Red
        $testPassed = $false
    }
}

# Test 2: Check Git repositories
Push-Location $productRepoPath
try {
    $productRemote = git remote get-url origin
    Write-Host "✅ Product repo remote: $productRemote" -ForegroundColor Green
} catch {
    Write-Host "❌ Product repo Git issue: $_" -ForegroundColor Red
    $testPassed = $false
}
Pop-Location

# Test 3: Python import test (if Python available)
try {
    python --version | Out-Null
    $pythonTest = python -c "import os, json, pathlib; print('Python environment OK')" 2>$null
    if ($pythonTest) {
        Write-Host "✅ Python environment test passed" -ForegroundColor Green
    }
} catch {
    Write-Host "⏭️  Python test skipped (not available)" -ForegroundColor Yellow
}

# =============================================================================
# Step 8: Generate Summary and Next Steps
# =============================================================================

Write-Host "`n📊 Setup Summary" -ForegroundColor Cyan
Write-Host "=================" -ForegroundColor Cyan

if ($testPassed) {
    Write-Host "🎉 Workspace setup completed successfully!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Workspace setup completed with warnings" -ForegroundColor Yellow
    Write-Host "   Please review the errors above and fix them manually" -ForegroundColor Yellow
}

Write-Host "`n📂 Workspace Structure:" -ForegroundColor White
Write-Host "  multi-agent-setup/                    # AI-team repository (this)" -ForegroundColor Gray
Write-Host "  ├── agents/                           # AI agent implementations" -ForegroundColor Gray
Write-Host "  ├── tools/                            # Tools for AI agents" -ForegroundColor Gray
Write-Host "  ├── workflows/                        # Agent coordination" -ForegroundColor Gray
Write-Host "  ├── workspace/                        # Cross-repo workspace" -ForegroundColor White
Write-Host "  │   └── $productRepoName/            # Product repository" -ForegroundColor White
Write-Host "  │       ├── docs/specs/               # 🎨 Speldesigner → UX specs" -ForegroundColor Cyan
Write-Host "  │       ├── frontend/src/components/  # 🔨 Utvecklare → React" -ForegroundColor Cyan
Write-Host "  │       └── backend/app/api/          # 🔨 Utvecklare → FastAPI" -ForegroundColor Cyan
Write-Host "  └── .env                              # Configuration" -ForegroundColor Gray

Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Configure your .env file with API keys:" -ForegroundColor White
Write-Host "   - ANTHROPIC_API_KEY=sk-ant-..." -ForegroundColor Gray
Write-Host "   - GITHUB_TOKEN=ghp_..." -ForegroundColor Gray

Write-Host "`n2. Test the setup with:" -ForegroundColor White
Write-Host "   python tests/integration/test_lifecycle_fixed.py" -ForegroundColor Gray

Write-Host "`n3. Start developing with AI agents:" -ForegroundColor White
Write-Host "   python -c `"from agents.projektledare import create_projektledare; print('AI team ready!')`"" -ForegroundColor Gray

Write-Host "`n4. Create your first feature request:" -ForegroundColor White
Write-Host "   - Go to GitHub Issues in multi-agent-setup repo" -ForegroundColor Gray
Write-Host "   - Use the 'Feature Request' template" -ForegroundColor Gray
Write-Host "   - AI team will automatically analyze and implement!" -ForegroundColor Gray

Write-Host "`n📚 Documentation:" -ForegroundColor Cyan
Write-Host "   - README.md                           # Getting started guide" -ForegroundColor Gray
Write-Host "   - docs/dna/                           # Project DNA documents" -ForegroundColor Gray
Write-Host "   - docs/setup/github_token_setup.md   # GitHub token instructions" -ForegroundColor Gray

Write-Host "`n✨ Happy AI development!" -ForegroundColor Magenta