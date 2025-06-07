"""
Contextual Tools for AI Agents
==============================

PURPOSE:
Dessa verktyg ger agenterna förmågan att förstå sin egen arbetsmiljö,
t.ex. att söka efter filer och förstå katalogstrukturen.
"""
from typing import Type
from crewai.tools import BaseTool # KORRIGERING: Ändrad från langchain_core.tools
from pydantic import BaseModel, Field
import os
from pathlib import Path

from config.settings import PROJECT_ROOT

class SearchInput(BaseModel):
    """Input för FileSearchTool."""
    query: str = Field(..., description="Filnamnet eller söktermen att leta efter.")

class FileSearchTool(BaseTool):
    name: str = "Filsökare"
    description: str = "Använd detta verktyg för att hitta den fullständiga, relativa sökvägen till en fil inom projektet. Perfekt när du vet vad en fil heter men inte var den ligger."
    args_schema: Type[BaseModel] = SearchInput

    def _run(self, query: str) -> str:
        """Söker igenom projektet och returnerar matchande filsökvägar."""
        results = []
        # Normalisera query för att hantera både filnamn och generella sökningar
        normalized_query = query.lower()
        
        for root, _, files in os.walk(str(PROJECT_ROOT)):
            # Undvik att söka i vissa kataloger för att minska brus
            if '.git' in root or '__pycache__' in root or 'node_modules' in root:
                continue
            
            for name in files:
                if normalized_query in name.lower():
                    full_path = Path(root) / name
                    # Säkerställ att sökvägen är relativ till projektroten
                    try:
                        relative_path = full_path.relative_to(PROJECT_ROOT)
                        results.append(str(relative_path).replace('\\', '/')) # Konsekvent med slash
                    except ValueError:
                        # Ignorera filer utanför projektroten
                        continue
        
        if not results:
            return f"Inga filer som matchar '{query}' hittades i projektet."
        
        return f"Hittade följande matchande filer:\n" + "\n".join(results)
