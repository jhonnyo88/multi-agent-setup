"""
DigiNativa AI-Agent: Speldesigner (Pedagogisk Arkitekt)
======================================================

PURPOSE:
Denna agent är teamets kreativa och pedagogiska kärna. Den tar emot analyserade
feature-requests från Projektledaren och omvandlar dem till detaljerade,
testbara och engagerande spelmekanik-specifikationer. Agentens främsta ansvar
är att säkerställa att all utveckling tjänar ett pedagogiskt syfte och är
perfekt anpassad för målgruppen "Anna".

KEY DEPENDENCIES:
- `docs/dna/design_principles.md`: Styr alla designbeslut.
- `docs/dna/target_audience.md`: Definierar "Anna" som primär användare.
- `docs/dna/architecture.md`: Sätter de tekniska ramarna.
- `docs/dna/vision_and_mission.md`: Ser till att designen är i linje med målen.

ADAPTATION GUIDE:
🔧 För att anpassa denna agent för ett annat projekt:
1.  Uppdatera `role` och `goal` för att reflektera din domän (t.ex. E-commerce UX Designer).
2.  I `backstory`, byt ut referenserna till de 5 designprinciperna och "Anna"
    mot din egen projektspecifika "DNA".
3.  Justera `tools` för att inkludera domänspecifika valideringsverktyg.
"""

from crewai import Agent
from langchain_anthropic import ChatAnthropic

# Projektimporter
from config.settings import AGENT_CONFIG, SECRETS
from tools.file_tools import FileReadTool, FileWriteTool
# TODO: Importera specialiserade designverktyg när de är skapade
from tools.design_tools import DesignPrinciplesValidatorTool, AcceptanceCriteriaValidatorTool
from tools.context_tools import FileSearchTool

class SpeldesignerAgent:
    def __init__(self):
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """
        Factory-funktion för att skapa Speldesigner-agenten.
        Denna agent är konfigurerad med en specifik personlighet och verktyg
        för att skapa högkvalitativa, pedagogiska spelspecifikationer.
        """
        # Konfigurera LLM (samma som för Projektledaren för konsistens)
        #
        claude_llm = ChatAnthropic(
            model=AGENT_CONFIG["llm_model"],
            api_key=SECRETS.get("anthropic_api_key"),
            temperature=AGENT_CONFIG["temperature"],
            max_tokens_to_sample=4000
        )

        return Agent(
            # Rollen är en kombination av titeln i PROJECT_SUMMARY.md och team_roles.md.
            # "Pedagogisk Arkitekt" betonar dess viktigaste funktion.
            role="Speldesigner (Pedagogisk Arkitekt)",

            # Målet är agentens primära direktiv: att skapa specifikationer som är
            # direkt användbara för utveckling och som följer alla projektets regler.
            goal=f"""
            Skapa exceptionellt detaljerade, engagerande och pedagogiska spel-specifikationer
            baserat på feature-requests. Varje specifikation måste vara en vattentät plan
            för Utvecklare och Testutvecklare och vara i linje med Definition of Done.
            Ditt arbete måste till punkt och pricka följa projektets 5 designprinciper och
            vara skräddarsytt för målgruppen "Anna".
            """,

            # Agentens "personlighet" och kunskapsbas. Den är instruerad att basera
            # alla sina beslut på de centrala DNA-dokumenten.
            backstory=f"""
            Du är en världsledande expert på "serious games" och "learning design", med en
            passion för att omvandla komplexa strategier till interaktiva och begripliga
            upplevelser. Ditt uppdrag i DigiNativa-teamet är att vara den kreativa
            kraften som säkerställer att varje funktion är både meningsfull och effektiv.

            Ditt arbete styrs av följande orubbliga regler från projektets DNA:

            1.  **De 5 Designprinciperna är din lag**:
                - **Pedagogik Framför Allt**: Varje element måste tjäna ett lärandemål.
                - **Policy till Praktik**: Koppla abstrakt strategi till verkligheten.
                - **Respekt för Tid**: Maximalt värde på under 10 minuter.
                - **Helhetssyn Genom Handling**: Lär ut systemtänk genom att göra.
                - **Intelligens, Inte Infantilisering**: En professionell och respektfull ton.

            2.  **Du designar för "Anna"**: En upptagen offentlig förvaltare med medelgod teknisk
            kunskap och extremt begränsad tid. Alla dina designer måste respektera detta.

            3.  **Teknisk Realism**: Dina specifikationer måste vara genomförbara med den
            valda tekniska stacken (React, FastAPI, Netlify).

            4.  **MVP-Fokus**: Dina första designer måste fokusera på kärnfunktionaliteten
            i "Strategibygget" för att leverera en första fungerande version snabbt.

            Ditt slutresultat är alltid en perfekt formaterad Markdown-fil som innehåller
            en komplett spelspecifikation, i enlighet med `feature_template.md`,
            inklusive syfte, spelmekanik, user stories och extremt tydliga, testbara acceptanskriterier.
            """,

            # Initiala verktyg. Dessa kommer att byggas ut med specialverktyg.
            tools=[
                FileReadTool(),   # För att läsa DNA-dokumenten
                FileWriteTool(),  # För att skapa specifikations-filerna
                # TODO: Lägg till DesignPrinciplesValidatorTool här
            ],

            llm=claude_llm,
            verbose=True,
            # Kan inte delegera, då denna agent är specialist på att skapa specifikationerna.
            allow_delegation=False,
            max_iterations=AGENT_CONFIG["max_iterations"]
        )

def create_speldesigner_agent() -> SpeldesignerAgent:
    return SpeldesignerAgent()
