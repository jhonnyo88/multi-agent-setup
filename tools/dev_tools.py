"""
Developer Tools for DigiNativa AI Agents
=========================================

PURPOSE:
Dessa verktyg ger AI-agenterna förmågan att interagera med Git och GitHub
för att hantera källkod, skapa branches, committa kod och skapa
pull requests.

ADAPTATION GUIDE:
🔧 För att anpassa dessa verktyg:
1.  Se till att GITHUB_TOKEN och repository-inställningarna i
    config/settings.py är korrekta för ditt projekt.
2.  Justera sökvägen till där du vill klona spel-repot.
"""

from typing import Type, Literal
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from pathlib import Path
import git
from github import Github

# Projektimporter
from config.settings import SECRETS, GITHUB_CONFIG, PROJECT_ROOT

# Sökväg för att lagra det lokala spel-repot
GAME_REPO_PATH = PROJECT_ROOT / "workspace" / "diginativa-game"

class GitToolInput(BaseModel):
    """Input för GitRepositoryTool."""
    command: Literal[
        'clone_or_pull', 'create_branch', 'add_commit', 'push', 'create_pr'
    ] = Field(..., description="Git-kommandot som ska utföras.")
    branch_name: str = Field(None, description="Namnet på branchen att skapa eller pusha.")
    commit_message: str = Field(None, description="Commit-meddelande.")
    pr_title: str = Field(None, description="Titel för pull request.")
    pr_body: str = Field(None, description="Beskrivning för pull request.")
    story_id: str = Field(None, description="ID för den story som arbetet gäller, används för branch-namn.")


class GitRepositoryTool(BaseTool):
    name: str = "Git-hanterare"
    description: str = "Ett verktyg för att hantera Git- och GitHub-operationer som att klona, skapa branch, committa, pusha och skapa pull requests."
    args_schema: Type[BaseModel] = GitToolInput
    repo: git.Repo = None
    github_repo = None

    def __init__(self):
        super().__init__()
        # Initiera GitHub API-klienten
        g = Github(SECRETS['github_token'])
        cfg = GITHUB_CONFIG['project_repo']
        self.github_repo = g.get_repo(f"{cfg['owner']}/{cfg['name']}")

    def _get_repo(self) -> git.Repo:
        """Hämtar eller klonar spel-repot och returnerar ett Repo-objekt."""
        if GAME_REPO_PATH.exists():
            self.repo = git.Repo(GAME_REPO_PATH)
        else:
            GAME_REPO_PATH.mkdir(parents=True, exist_ok=True)
            repo_url = f"https://{SECRETS['github_token']}@github.com/{GITHUB_CONFIG['project_repo']['owner']}/{GITHUB_CONFIG['project_repo']['name']}.git"
            self.repo = git.Repo.clone_from(repo_url, GAME_REPO_PATH)
        return self.repo

    def _run(self, command: str, **kwargs) -> str:
        """Kör det specificerade git-kommandot."""
        repo = self._get_repo()
        
        if command == 'clone_or_pull':
            repo.remotes.origin.pull('main')
            return f"Repositoryt är uppdaterat med senaste från main-branchen."
        
        elif command == 'create_branch':
            branch_name = kwargs.get('branch_name')
            if not branch_name:
                 # Skapa ett standardiserat branch-namn om inget anges
                 story_id = kwargs.get('story_id', 'generic-work')
                 branch_name = f"feature/{story_id}"

            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
            return f"Skapade och checkade ut ny branch: {branch_name}"

        elif command == 'add_commit':
            if not repo.is_dirty(untracked_files=True):
                return "Inga ändringar att committa."
            repo.git.add(A=True)
            repo.index.commit(kwargs.get('commit_message', 'AI-genererad commit'))
            return f"Committade ändringar med meddelandet: '{kwargs.get('commit_message')}'"

        elif command == 'push':
            branch_name = kwargs.get('branch_name')
            repo.remotes.origin.push(branch_name, set_upstream=True)
            return f"Pushade branch '{branch_name}' till remote repository."

        elif command == 'create_pr':
            try:
                pr = self.github_repo.create_pull(
                    title=kwargs.get('pr_title'),
                    body=kwargs.get('pr_body'),
                    head=kwargs.get('branch_name'),
                    base=GITHUB_CONFIG['project_repo']['branch']
                )
                return f"Skapade Pull Request #{pr.number}: {pr.html_url}"
            except Exception as e:
                return f"Kunde inte skapa Pull Request. Det kan redan finnas en för denna branch. Fel: {e}"
        
        return f"Okänt kommando: {command}"