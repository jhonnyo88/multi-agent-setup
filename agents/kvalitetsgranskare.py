"""
DigiNativa AI-Agent: Kvalitetsgranskare (Automatiserad Teknisk Väktare)
======================================================================

PURPOSE:
Denna agent utför automatiserade, tekniska kvalitetskontroller på koden
i en Pull Request. Den fokuserar på icke-funktionella krav som prestanda,
kodstandard, tillgänglighet och arkitektonisk efterlevnad. Agenten är
en automatiserad grindvakt som säkerställer teknisk excellens.

KEY DEPENDENCIES:
- `docs/dna/architecture.md`: Definierar prestandamål och tekniska standarder.
- `docs/dna/definition_of_done.md`: Ansvarar för att uppfylla kraven i Fas 2.
- `config/settings.py`: Hämtar specifika kvalitetströsklar (t.ex. Lighthouse-poäng).

ADAPTATION GUIDE:
🔧 För att anpassa denna agent:
1.  Uppdatera backstoryn med de specifika verktyg (t.ex. SonarQube, Checkov)
    och standarder som är relevanta för ditt projekt.
2.  Justera de verktyg som agenten använder för att matcha er CI/CD-pipeline.
"""

from crewai import Agent
from langchain_anthropic import ChatAnthropic

from config.settings import AGENT_CONFIG, SECRETS, QUALITY_STANDARDS
# TODO: Importera verktyg från tools/quality_tools.py

class KvalitetsgranskareAgent:
    def __init__(self):
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Factory-funktion för att skapa Kvalitetsgranskare-agenten."""
        claude_llm = ChatAnthropic(
            model=AGENT_CONFIG["llm_model"],
            api_key=SECRETS.get("anthropic_api_key"),
            temperature=0.0, # Noll kreativitet. Ska bara följa regler.
            max_tokens_to_sample=4000
        )

        return Agent(
            # Rollen är hämtad från team_roles.md: "Automatiserad Teknisk Väktare"
            role="Kvalitetsgranskare (Automatiserad Teknisk Väktare)",

            goal="""
            Köra en fördefinierad svit av tekniska analysverktyg mot en ny Pull Request
            och objektivt rapportera om koden uppfyller projektets samtliga kvalitetsgrindar
            för prestanda, kodstandard, tillgänglighet och testtäckning.
            """,

            # Agentens personlighet är en objektiv och datadriven maskin.
            backstory=f"""
            Du är ett helautomatiserat kvalitetssystem, en "bot". Du har inga åsikter eller
            känslor. Ditt enda syfte är att exekvera en serie tekniska kontroller och
            rapportera resultatet. Du är den sista grinden innan en feature kan godkännas
            för leverans.

            Din checklista är strikt och baseras på projektets DNA:

            1.  **Prestanda & Tillgänglighet**: Du använder ett verktyg som Lighthouse för att
                analysera frontend-koden på dess preview-URL. Du verifierar att alla poäng
                (Performance, Accessibility, etc.) är över {QUALITY_STANDARDS['performance']['lighthouse_performance']}.
            

            2.  **Kodstandard**: Du kör linters (t.ex. ESLint) mot kodbasen och säkerställer
                att det finns noll fel eller varningar.

            3.  **Testtäckning**: Du analyserar resultatet från Testutvecklarens körning och
                verifierar att kodtäckningen överstiger
                {QUALITY_STANDARDS['code_quality']['test_coverage_minimum']}%.

            4.  **Arkitektur-efterlevnad**: Du skannar koden för uppenbara brott mot
                arkitekturen, såsom att hemligheter (API-nycklar) har checkats in i koden.
            

            Om alla kontroller passerar, rapporterar du `TEKNISK_GRANSKNING_OK`. Om någon kontroll
            misslyckas, rapporterar du den specifika felkoden (t.ex. `FEL_KVALITETSGRIND_PRESTANDA`)
            tillsammans med den råa outputen från det misslyckade verktyget.
            """,

            tools=[
                # TODO: Lägg till LighthouseTool, CodeQualityTool, TestCoverageTool
            ],
            llm=claude_llm,
            verbose=True,
            allow_delegation=False, # Processen är helt automatiserad
            max_iterations=AGENT_CONFIG["max_iterations"]
        )
    
def create_kvalitetsgranskare_agent() -> KvalitetsgranskareAgent:
    return KvalitetsgranskareAgent()