"""
End-to-End Test för Hela AI-Teamets Arbetsflöde
"""
import asyncio
import json
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from crewai import Crew, Process, Task
from agents.projektledare import create_projektledare
from agents.speldesigner import create_speldesigner_agent
from agents.utvecklare import create_utvecklare_agent
from agents.testutvecklare import create_testutvecklare_agent
from agents.qa_testare import create_qa_testare_agent
from agents.kvalitetsgranskare import create_kvalitetsgranskare_agent
from tools.file_tools import read_file
from config.settings import PROJECT_ROOT

REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
(REPORTS_DIR / "specs").mkdir(exist_ok=True)

def print_section(title: str):
    print(f"\n{'='*70}\n🚀 {title}\n{'='*70}")

def print_success(message: str):
    print(f"✅ {message}")

def print_info(message: str):
    print(f"ℹ️  {message}")

async def test_full_lifecycle():
    print_section("Startar End-to-End Test av Hela AI-Teamet")

    # --- STEG 1: FÖRBEREDELSER OCH INPUT ---
    projektledare_wrapper = create_projektledare()
    mock_github_issue = {
        "number": 123,
        "title": "Add user progress tracking to game",
        "body": "As Anna, I want to see my progress to understand what I've learned, respecting my time and intelligence.",
    }
    feature_analysis = await projektledare_wrapper.analyze_feature_request(mock_github_issue)

    # --- STEG 2: INSTANSIERA HELA TEAMET ---
    speldesigner = create_speldesigner_agent()
    utvecklare = create_utvecklare_agent()
    testutvecklare = create_testutvecklare_agent()
    qa_testare = create_qa_testare_agent()
    kvalitetsgranskare = create_kvalitetsgranskare_agent()
    
    # --- STEG 3: DEFINIERA HELA UPPGIFTSKEDJAN ---
    
    # KORRIGERING HÄR: Hämta 'number' direkt från mock-objektet.
    spec_file_path_str = f"reports/specs/spec_F{mock_github_issue['number']}.md"
    spec_file_path = REPORTS_DIR / "specs" / f"spec_F{mock_github_issue['number']}.md"


    # Uppgift för Speldesigner
    spec_task = Task(
        description=f"Skapa en detaljerad spelspecifikation för featuren 'User Progress Tracking', baserat på följande analys:\n---\n{json.dumps(feature_analysis, indent=2, ensure_ascii=False)}\n---",
        expected_output=f"En sökväg till den skapade MD-filen: '{spec_file_path_str}'",
        agent=speldesigner.agent
    )

    # Uppgift för Utvecklare
    dev_task = Task(
        description=f"Implementera koden (både frontend och backend) enligt specifikationen som finns i filen specificerad av föregående uppgift.",
        expected_output="En commit med den nya koden i en feature-branch.",
        agent=utvecklare.agent,
        context=[spec_task]
    )

    # Uppgift för Testutvecklare
    test_dev_task = Task(
        description="Skriv automatiserade tester (Pytest) som verifierar alla acceptanskriterier i specifikationen från föregående uppgifter.",
        expected_output="En commit med nya testfiler i samma feature-branch.",
        agent=testutvecklare.agent,
        context=[spec_task]
    )

    # Uppgift för QA-Testare
    qa_task = Task(
        description="Genomför en funktionell granskning av featuren från 'Annas' perspektiv. Anta att du har fått en preview-URL.",
        expected_output="En QA-rapport (antingen 'Godkänd' eller en buggrapport).",
        agent=qa_testare.agent,
        context=[dev_task, test_dev_task]
    )
    
    # Uppgift för Kvalitetsgranskare
    quality_task = Task(
        description="Kör automatiserade tekniska granskningar (t.ex. Lighthouse) mot featurens preview-URL.",
        expected_output="En teknisk rapport med prestanda- och kvalitets-poäng.",
        agent=kvalitetsgranskare.agent,
        context=[qa_task]
    )

    # Uppgift för Projektledare att slutföra
    pr_task = Task(
        description="Om alla tidigare steg är godkända, skapa en Pull Request på GitHub.",
        expected_output="En URL till den nyskapade Pull Requesten.",
        agent=projektledare_wrapper.agent,
        context=[quality_task]
    )

    # --- STEG 4: SKAPA OCH KÖR HELA CREW:ET ---
    full_crew = Crew(
        agents=[
            projektledare_wrapper.agent, 
            speldesigner.agent, 
            utvecklare.agent, 
            testutvecklare.agent, 
            qa_testare.agent, 
            kvalitetsgranskare.agent
        ],
        tasks=[spec_task, dev_task, test_dev_task, qa_task, quality_task, pr_task],
        process=Process.sequential,
        verbose=True
    )

    print("\n>>> Startar hela arbetsflödet... Detta kan ta flera minuter. <<<")
    result = full_crew.kickoff()

    # --- STEG 5: VISA SLUTRESULTATET ---
    print_section("Resultat från Hela Arbetsflödet")
    print(f"Teamets slutrapport:\n{result}")

    if result and "pull" in result.lower() and "github.com" in result.lower():
        print_success(f"Testet slutfördes och en Pull Request-länk genererades!")
    else:
        print(f"❌ Testet slutfördes, men outputen verkar inte vara en Pull Request-länk. Kontrollera loggen för fel.")


if __name__ == "__main__":
    asyncio.run(test_full_lifecycle())