# GitHub Token Setup Guide

## Creating a GitHub Personal Access Token

1. Go to GitHub.com and sign in
2. Click your profile picture → Settings
3. In the left sidebar, click "Developer settings"
4. Click "Personal access tokens" → "Tokens (classic)"
5. Click "Generate new token"

## Required Permissions

For the DigiNativa AI team to work properly, the token needs these permissions:

- ✅ **repo** - Full control of private repositories
- ✅ **issues** - Read and write issues and comments
- ✅ **pull_requests** - Read and write pull requests

## Adding Token to Project

1. Copy your generated token (starts with `ghp_`)
2. Open `.env` file in your project root
3. Add this line: `GITHUB_TOKEN=ghp_your_actual_token_here`
4. Save the file

## Testing Your Setup

Run this command to test your GitHub connection:

```bash
python tests/test_github_integration/test_connection.py