"""
Specialized Design Tools for DigiNativa AI Agents
==================================================

PURPOSE:
Dessa verktyg ger Speldesigner-agenten kognitiva förmågor för att
validera sina egna specifikationer mot projektets kärnprinciper (DNA).
Detta säkerställer att all design är av hög kvalitet och i linje
med projektets mål innan den överlämnas till utveckling.

ADAPTATION GUIDE:
🔧 För att anpassa dessa verktyg:
1.  Uppdatera `_run`-metoden i `DesignPrinciplesValidatorTool` för att
    referera till dina egna designprinciper.
2.  Justera prompten i `AcceptanceCriteriaValidatorTool` för att
    matcha dina kvalitetskrav på acceptanskriterier.
"""
from typing import List, Type
import os
import json

# Ny, korrekt rad:
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_anthropic import ChatAnthropic

# Importera relevanta konstanter från projektets inställningar
from config.settings import AGENT_CONFIG, SECRETS, DNA_DIR
from tools.file_tools import read_file

# --- Pydantic Input Models för Verktygen ---

class DesignReviewInput(BaseModel):
    """Input för DesignPrinciplesValidatorTool."""
    specification_text: str = Field(..., description="Den fullständiga texten för den designspecifikation som ska granskas.")

class AcceptanceCriteriaInput(BaseModel):
    """Input för AcceptanceCriteriaValidatorTool."""
    acceptance_criteria: List[str] = Field(..., description="En lista med acceptanskriterier som ska valideras.")

# --- Specialiserade Verktyg ---

class DesignPrinciplesValidatorTool(BaseTool):
    """
    Ett verktyg för att granska en designspecifikation mot projektets
    fem kärndesignprinciper.
    """
    name: str = "Designprincip-granskare"
    description: str = "Använd detta verktyg för att validera en designspecifikation mot de fem designprinciperna. Verktyget ger poäng och motivering för varje princip."
    args_schema: Type[BaseModel] = DesignReviewInput
    claude_llm: ChatAnthropic = None

    def __init__(self):
        super().__init__()
        # Initiera LLM för verktygets interna logik
        self.claude_llm = ChatAnthropic(
            model=AGENT_CONFIG["llm_model"],
            api_key=SECRETS.get("anthropic_api_key")
        )

    def _run(self, specification_text: str) -> str:
        """Kör valideringslogiken."""
        try:
            # Läs in de aktuella designprinciperna direkt från DNA-dokumentet
            #
            principles_path = DNA_DIR / "design_principles.md"
            principles_content = read_file(str(principles_path), agent_name="speldesigner")

            prompt = f"""
            Du är en Senior UX-granskare. Ditt uppdrag är att utvärdera följande designspecifikation
            mot projektets 5 kärnprinciper.

            HÄR ÄR DE 5 DESIGNPRINCIPERNA:
            ---
            {principles_content}
            ---

            HÄR ÄR DESIGNSPECIFIKATIONEN SOM SKA GRANSKAS:
            ---
            {specification_text}
            ---

            Instruktioner:
            För varje designprincip, ge ett betyg från 1 (efterlevs inte alls) till 5 (perfekt efterlevnad).
            Ge en kort, konkret motivering för ditt betyg.
            Svara ENDAST med en JSON-formaterad sträng som följer detta schema:
            {{
                "principle_1_pedagogy": {{ "score": <int>, "motivation": "<string>" }},
                "principle_2_policy_to_practice": {{ "score": <int>, "motivation": "<string>" }},
                "principle_3_time_respect": {{ "score": <int>, "motivation": "<string>" }},
                "principle_4_holistic_view": {{ "score": <int>, "motivation": "<string>" }},
                "principle_5_intelligence_not_infantilization": {{ "score": <int>, "motivation": "<string>" }}
            }}
            """

            response = self.claude_llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Ett fel uppstod vid granskning av designprinciper: {str(e)}"


class AcceptanceCriteriaValidatorTool(BaseTool):
    """
    Ett verktyg för att säkerställa att acceptanskriterier är tydliga,
    testbara och uppfyller Definition of Done.
    """
    name: str = "Acceptanskriterie-granskare"
    description: str = "Använd detta verktyg för att validera en lista av acceptanskriterier. Verktyget säkerställer att varje kriterium är specifikt, mätbart och testbart."
    args_schema: Type[BaseModel] = AcceptanceCriteriaInput
    claude_llm: ChatAnthropic = None
    
    def __init__(self):
        super().__init__()
        self.claude_llm = ChatAnthropic(
            model=AGENT_CONFIG["llm_model"],
            api_key=SECRETS.get("anthropic_api_key")
        )

    def _run(self, acceptance_criteria: List[str]) -> str:
        """Kör valideringslogiken."""
        try:
            prompt = f"""
            Du är en QA Lead med expertis i att skriva testbara krav. Ditt uppdrag är att
            granska följande lista med acceptanskriterier.

            LISTA MED ACCEPTANSKRITERIER:
            ---
            {json.dumps(acceptance_criteria, indent=2, ensure_ascii=False)}
            ---

            Instruktioner:
            För varje kriterium, utvärdera om det är specifikt, mätbart och testbart.
            Svara ENDAST med en JSON-formaterad lista av objekt, där varje objekt följer detta schema:
            {{
                "criterion": "<det ursprungliga kriteriet>",
                "is_testable": <boolean>,
                "suggestion_for_improvement": "<en konkret förbättring om is_testable är false, annars en tom sträng>"
            }}
            """
            response = self.claude_llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Ett fel uppstod vid granskning av acceptanskriterier: {str(e)}"