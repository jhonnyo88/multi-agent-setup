"""
Code Quality & Performance Tools for AI Agents
==============================================

PURPOSE:
Verktyg som gör det möjligt för Kvalitetsgranskare-agenten att köra
automatiserade tester för prestanda, kodkvalitet och testtäckning.
"""
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import subprocess
import json

class QualityToolInput(BaseModel):
    """Input för kvalitetsverktyg."""
    target_url: str = Field(None, description="URL till Netlify preview-miljön som ska testas.")
    repo_path: str = Field(None, description="Lokal sökväg till git-repot som ska analyseras.")


class LighthouseTool(BaseTool):
    name: str = "Lighthouse Prestanda-testare"
    description: str = "Kör ett Lighthouse-test mot en given URL och returnerar prestanda-poängen."
    args_schema: Type[BaseModel] = QualityToolInput

    def _run(self, target_url: str) -> str:
        """Kör Lighthouse CLI och returnerar en sammanfattning."""
        try:
            # Förutsätter att lighthouse är installerat globalt: `npm install -g lighthouse`
            command = [
                "lighthouse",
                target_url,
                "--output=json",
                "--output-path=stdout",
                "--only-categories=performance,accessibility,best-practices,seo",
                "--chrome-flags='--headless --no-sandbox'"
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=True, shell=True)
            report = json.loads(result.stdout)
            
            scores = {
                category: data['score'] * 100 
                for category, data in report['categories'].items()
            }
            return json.dumps(scores, indent=2)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            return f"Kunde inte köra Lighthouse. Se till att 'lighthouse' är installerat och tillgängligt i PATH. Fel: {e}"
        except Exception as e:
            return f"Ett oväntat fel uppstod med Lighthouse: {e}"

# Placeholder för andra verktyg som CodeQualityTool och TestCoverageTool.
# Deras implementation skulle likna LighthouseTool men anropa verktyg som
# ESLint, Pytest-cov etc. och returnera deras resultat.