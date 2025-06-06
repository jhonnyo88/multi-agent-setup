"""
Isolerat Test-script för Speldesigner-agenten
=============================================

SYFTE:
Detta script verifierar att Speldesigner-agenten kan ta emot en uppgift,
använda sina specialiserade verktyg för att utföra den, och producera
en högkvalitativ designspecifikation i enlighet med projektets DNA.

VAD DETTA TESTAR:
1.  Agentens förmåga att förstå en uppgift från Projektledaren.
2.  Användningen av `DesignPrinciplesValidatorTool` för att självgranska.
3.  Användningen av `AcceptanceCriteriaValidatorTool` för att skapa testbara krav.
4.  Användningen av `FileWriteTool` för att spara den slutgiltiga artefakten.
5.  Den övergripande kvaliteten och strukturen på den genererade specifikationen.
"""

import asyncio
import json
from pathlib import Path
import sys
import os

# Lägg till projektroten i sökvägen för att kunna importera moduler
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from crewai import Task, Crew

# Importera agent-fabriker och verktyg
from agents.projektledare import create_projektledare
from agents.speldesigner import create_speldesigner_agent
from tools.file_tools import read_file
# Antagande: Vi lägger till en REPORTS_DIR i settings.py för att hantera artefakter
from tools.context_tools import FileSearchTool
from config.settings import PROJECT_ROOT

# Definiera och säkerställ att rapport-katalogen finns
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
(REPORTS_DIR / "specs").mkdir(exist_ok=True)


def print_section(title: str):
    print(f"\n{'='*60}\n🧪 {title}\n{'='*60}")

def print_success(message: str):
    print(f"✅ {message}")

def print_info(message: str):
    print(f"ℹ️  {message}")

async def test_speldesigner_specification_task():
    """
    Testar Speldesigner-agentens hela arbetsflöde för att skapa en spec.
    """
    print_section("Testar Speldesigner-agentens specifikations-uppgift")

    # --- STEG 1: SETUP ---
    # Simulera input från Projektledaren.
    print_info("Simulerar input från Projektledaren...")
    projektledare = create_projektledare()
    mock_github_issue = {
        "number": 123, "title": "Add user progress tracking to game",
        "body": "As Anna, I want to see my progress to understand what I've learned."
    }
    feature_analysis = await projektledare.analyze_feature_request(mock_github_issue)
    print_success("Input från Projektledaren simulerad.")

    # --- STEG 2: DEFINIERA UPPGIFTEN ---
    # Skapa Speldesigner-agenten med sina verktyg
    speldesigner = create_speldesigner_agent()

    spec_file_path = REPORTS_DIR / "specs" / f"spec_F{mock_github_issue['number']}.md"
    
    design_task = Task(
        description=f"""
    Din uppgift är att skapa en komplett designspecifikation för featuren
    "User Progress Tracking", baserat på den bifogade feature-analysen.

    Analys från Projektledaren:
    ---
    {json.dumps(feature_analysis, indent=2, ensure_ascii=False)}
    ---

    VIKTIG ARBETSPROCESS: Du måste följa dessa steg i exakt ordning.
    1.  **OBLIGATORISKT FÖRSTA STEG:** Du vet inte var DNA-filerna finns. Använd
        verktyget `Filsökare` för att hitta de exakta, relativa sökvägarna till
        `design_principles.md` och `target_audience.md`. Använd INTE `file_read_tool`
        förrän du har en fullständig sökväg från `Filsökare`.
    2.  Använd `file_read_tool` med de sökvägar du hittade för att läsa dokumenten.
    3.  Skriv ett första utkast till en komplett specifikation.
    4.  Använd dina valideringsverktyg (`AcceptanceCriteriaValidatorTool` och
        `DesignPrinciplesValidatorTool`) för att granska och iterativt förbättra
        ditt utkast tills det uppfyller alla kvalitetskrav.
    5.  När specifikationen är validerad och klar, använd `FileWriteTool` för att
        spara den till den relativa sökvägen: 'reports/specs/spec_F123.md'.
    """,
        expected_output=f"En bekräftelse på att den färdiga och validerade specifikationen har sparats till 'reports/specs/spec_F123.md'.",
        agent=speldesigner
    )

    # --- STEG 3: KÖR UPPGIFTEN ---
    print_info(f"Startar Speldesigner-agenten...")
    game_design_crew = Crew(
        agents=[speldesigner],
        tasks=[design_task],
        verbose=True
    )
    result = game_design_crew.kickoff()

    # --- STEG 4: VERIFIERA RESULTATET ---
    print_section("Resultat av Speldesigner-test")
    print_info(f"Agentens slutrapport: {result}")

    if spec_file_path.exists() and spec_file_path.stat().st_size > 0:
        print_success(f"Specifikationsfilen skapades korrekt på: {spec_file_path}")
        spec_content = read_file(str(spec_file_path), agent_name="test_runner")
        print_info("--- Start på specifikationsfil ---")
        print(spec_content[:1000] + "...")
        print("--- Slut på specifikationsfil ---")
    else:
        print(f"❌ FEL: Specifikationsfilen '{spec_file_path}' skapades inte eller är tom.")

async def main():
    await test_speldesigner_specification_task()

if __name__ == "__main__":
    asyncio.run(main())