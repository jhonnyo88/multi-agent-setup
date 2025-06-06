"""
Contextual Tools for AI Agents
==============================

PURPOSE:
Dessa verktyg ger agenterna förmågan att förstå sin egen arbetsmiljö,
t.ex. att söka efter filer och förstå katalogstrukturen.
"""
from typing import Type
from langchain_core.tools import BaseTool
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
        for root, _, files in os.walk(str(PROJECT_ROOT)):
            for name in files:
                if query in name:
                    full_path = Path(root) / name
                    relative_path = full_path.relative_to(PROJECT_ROOT)
                    results.append(str(relative_path).replace('\\', '/')) # Konsekvent med slash
        
        if not results:
            return f"Inga filer som matchar '{query}' hittades i projektet."
        
        return f"Hittade följande matchande filer:\n" + "\n".join(results)