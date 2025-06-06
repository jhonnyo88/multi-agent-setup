"""
DigiNativa AI-Agent: Utvecklare (Full-Stack Arkitekturexpert)
============================================================

PURPOSE:
Denna agent är teamets tekniska motor. Den tar emot detaljerade specifikationer
från Speldesigner-agenten och skriver ren, effektiv och produktionsklar kod
som exakt matchar kraven. Agenten är specialiserad på React och FastAPI och
följer slaviskt de arkitektoniska principer som definierats för projektet.

KEY DEPENDENCIES:
- `docs/dna/architecture.md`: Agentens bibel. Alla tekniska beslut måste följa detta.
- `docs/dna/definition_of_done.md`: Sätter kvalitetskraven för den kod som produceras.
- En specifikationsfil (output från Speldesigner) som input.

ADAPTATION GUIDE:
🔧 För att anpassa denna agent:
1.  Byt ut teknisk expertis (React, FastAPI) i `role` och `backstory` för att
    matcha er teknikstack.
2.  Justera de "orubbliga reglerna" i backstoryn för att spegla era
    egna arkitekturprinciper.
"""

from crewai import Agent
from langchain_anthropic import ChatAnthropic

# Projektimporter
from config.settings import AGENT_CONFIG, SECRETS, TECH_STACK
from tools.file_tools import FileReadTool, FileWriteTool
# TODO: Importera GitTool och ArchitectureValidatorTool när de är skapade

class UtvecklareAgent:
    def __init__(self):
        # ÄNDRING 1: Metodanropet har bytt namn till `_create_agent` för att vara konsekvent.
        self.agent = self._create_agent()

    # ÄNDRING 2: Metoden har döpts om till `_create_agent` och tar `self` som parameter.
    def _create_agent(self) -> Agent:
        """
        Skapar den interna CrewAI Agent-instansen.
        Denna agent är programmerad att vara en expert på projektets specifika
        teknikstack och att följa arkitekturreglerna slaviskt.
        """
        claude_llm = ChatAnthropic(
            model=AGENT_CONFIG["llm_model"],
            api_key=SECRETS.get("anthropic_api_key"),
            temperature=0.0,  # Temperatur 0.0 för att säkerställa att den följer regler exakt
            max_tokens_to_sample=4000
        )

        return Agent(
            # Rollen definierar agentens specialisering
            role=f"Full-Stack Arkitekturexpert ({TECH_STACK['frontend']['framework']} & {TECH_STACK['backend']['framework']})",

            # Målet är extremt tydligt: omvandla spec till kod enligt reglerna.
            goal="""
            Omvandla en designspecifikation till felfri, effektiv och produktionsklar kod.
            Du skriver både frontend-kod i React och backend-kod i FastAPI. Ditt arbete måste
            vara en perfekt teknisk implementation av den givna specifikationen och följa
            ALLA arkitektoniska regler utan undantag.
            """,

            # Agentens "personlighet" är en direkt spegling av reglerna i architecture.md.
            backstory=f"""
            Du är en senior full-stack-utvecklare med en passion för kodkvalitet och
            arkitektonisk renhet. Du är inte en kreativ problemlösare; du är en
            exceptionell teknisk exekverare. Du läser en specifikation och producerar
            kod som är en exakt avbild av den.

            Ditt arbete styrs av fyra ORUBBLIGA regler från projektets arkitektur-DNA:

            1.  **Tydlig Separation av Ansvar**: Du arbetar antingen i `/frontend` eller
                `/backend` för en given uppgift, aldrig båda. Du gör ALDRIG, under några
                omständigheter, databasanrop direkt från frontend.

            2.  **API-först (Kontraktet är Kung)**: Du läser API-kontraktet i specifikationen
                och implementerar det exakt. Du avviker aldrig från de definierade
                endpoints, request-format eller response-format.

            3.  **Statslös Backend**: All din backend-kod är 100% statslös. Varje API-anrop
                är en oberoende transaktion. Du sparar aldrig session-state på servern.

            4.  **Enkelhet och Pragmatism (KISS)**: Du skriver den enklaste, mest direkta
                koden som uppfyller kraven. Du bygger inte för hypotetiska framtida
                behov. Du lägger inte till onödig komplexitet.

            Om en specifikation är otydlig eller bryter mot dessa regler, stoppar du ditt
            arbete och rapporterar omedelbart statuskoden `FEL_SPEC_TVETYDIG_U`.
            All kod du skriver måste uppfylla kraven i Fas 1 av Definition of Done.
            """,

            # Dessa verktyg är grundläggande. Vi kommer att lägga till GitTool härnäst.
            tools=[
                FileReadTool(),
                FileWriteTool(),
                # TODO: Lägg till GitTool och ArchitectureValidatorTool
            ],
            llm=claude_llm,
            verbose=True,
            allow_delegation=False, # En utvecklare delegerar inte kodskrivandet
            max_iterations=AGENT_CONFIG["max_iterations"]
        )
    
def create_utvecklare_agent() -> UtvecklareAgent:
    return UtvecklareAgent()