#!/usr/bin/env python3
"""Förenklad setup för DigiNativa AI-Team"""

import os
from pathlib import Path
from dotenv import load_dotenv

def main():
    print("🚀 DigiNativa Setup")
    
    # Skapa .env om den inte finns
    if not Path(".env").exists():
        with open(".env", "w") as f:
            f.write("OPENAI_API_KEY=your_key_here\n")
            f.write("GITHUB_TOKEN=your_token_here\n")
        print("✅ .env skapad - fyll i dina API-nycklar")
    else:
        print("✅ .env finns redan")
    
    print("🎉 Setup klar!")

if __name__ == "__main__":
    main()