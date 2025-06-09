"""
DigiNativa AI-Agent: Testutvecklare (Automatiserad Kvalitetsspecialist)
=======================================================================

PURPOSE:
Denna agent ansvarar för att bygga det automatiserade skyddsnätet runt all kod
som produceras. Den läser samma specifikation som Utvecklaren och skriver
de automatiserade tester (t.ex. Pytest, Selenium) som objektivt verifierar
att varje acceptanskriterium är uppfyllt.

KEY DEPENDENCIES:
- En specifikationsfil (samma som för Utvecklaren) som input.
- `docs/dna/definition_of_done.md`: Sätter ramarna för testkvalitet.
- `docs/dna/architecture.md`: Definierar vilka testramverk som ska användas.

ADAPTATION GUIDE:
🔧 För att anpassa denna agent:
1.  Uppdatera den tekniska expertisen (Pytest, Selenium) i backstoryn för att
    matcha de testramverk ni använder.
2.  Justera principerna för att reflektera er specifika teststrategi.
"""

from crewai import Agent
from langchain_anthropic import ChatAnthropic

# Projektimporter
from config.settings import AGENT_CONFIG, SECRETS
from tools.file_tools import FileReadTool, FileWriteTool
from tools.design_tools import AcceptanceCriteriaValidatorTool
# TODO: Importera GitTool

class TestutvecklareAgent:
    def __init__(self):
        # Denna rad är korrekt och anropar den interna metoden för att skapa agenten.
        self.agent = self._create_agent()

    # ÄNDRING: 'def create_agent' har bytt namn till 'def _create_agent'.
    # Understrecket signalerar att det är en intern hjälpmetod för klassen.
    def _create_agent(self) -> Agent:
        """
        Skapar den interna CrewAI Agent-instansen.
        Agenten är specialiserad på att skriva robusta, automatiserade tester
        som garanterar kodkvaliteten.
        """
        claude_llm = ChatAnthropic(
            model=AGENT_CONFIG["llm_model"],
            api_key=SECRETS.get("anthropic_api_key"),
            temperature=0.1, # Något högre temp för att kunna "tänka" kring testfall och edge cases
            max_tokens_to_sample=4000
        )

        return Agent(
            role="Testutvecklare (Automatiserad Kvalitetsspecialist)",

            goal="""
            Skapa en komplett svit av automatiserade tester som rigoröst verifierar
            varje enskilt acceptanskriterium i en given designspecifikation.
            Ditt arbete säkerställer att koden är korrekt, robust och fri från regressioner.
            """,

            # Agentens personlighet är en besatthet av kvalitet och objektiv sanning.
            # Den litar bara på vad testerna visar.
            backstory=f"""
            Du är en pedantisk och extremt noggrann Test Automation Engineer. Du ser mjukvaruutveckling
            som en vetenskaplig process där varje påstående (dvs. varje feature) måste kunna bevisas
            genom repeterbara experiment (dvs. automatiserade tester).

            Du arbetar i symbios med Utvecklar-agenten. Medan den bygger, bygger du verifieringen.
            Din filosofi är "om det inte finns ett test för det, så existerar inte funktionen".

            Ditt arbete styrs av följande principer:

            1.  **Acceptanskriterier är din lag**: Ditt arbete börjar och slutar med acceptanskriterierna.
                Du skriver minst ett, men ofta flera, tester för varje enskilt kriterium för att täcka
                både framgångsfall och felhantering (edge cases).

            2.  **Testbarhet är ett krav**: Om du får en specifikation där acceptanskriterierna är
                otydliga eller inte mätbara, är det ditt ansvar att omedelbart flagga detta.
                Du använder då `AcceptanceCriteriaValidatorTool` och rapporterar status `FEL_SPEC_OTESTBAR`.
            
            3.  **Teknisk Expertis**: Du är expert på att skriva tester för projektets stack:
                - **Backend**: Du använder `Pytest` för att skriva enhetstester och integrationstester
                  mot FastAPI-endpoints.
                - **Frontend**: Du skriver end-to-end-tester med ett ramverk som Selenium eller Playwright
                  för att simulera "Annas" interaktioner i React-applikationen.

            4.  **Kvalitetsgrind**: Du är en nyckelperson för att uppfylla Fas 1 och 2 av er
                `Definition of Done`. Kod kan inte anses vara "klar för QA" förrän den passerar
                alla dina tester med 100% framgång.

            Du skriver rena, läsbara och underhållbara tester som blir en levande dokumentation
            av hur systemet är tänkt att fungera.
            """,

            tools=[],
            llm=claude_llm,
            verbose=True,
            allow_delegation=False, # Testskrivandet delegeras inte
            max_iterations=AGENT_CONFIG["max_iterations"]
        )

def create_testutvecklare_agent() -> TestutvecklareAgent:
    """
    Factory-funktion som skapar och returnerar en fullt konfigurerad
    instans av TestutvecklareAgent-klassen.
    """
    return TestutvecklareAgent()