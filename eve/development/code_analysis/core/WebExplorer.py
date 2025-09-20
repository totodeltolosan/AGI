import requests
from bs4 import BeautifulSoup
from SupervisorInterface import SupervisorInterface  # Pour les type hints


class WebExplorer:
    """EXPLORATEUR WEB - Collecteur de données depuis Wikipedia"""

    def __init__(self, supervisor: SupervisorInterface):
        """TODO: Add docstring."""
        self.supervisor = supervisor
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    """TODO: Add docstring."""
    def explore_url(self, url: str) -> tuple[list, str] | None:
        self.supervisor.display_info(f"🌐 Exploration de l'URL: {url}")
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            links = []
            text_content = ""
            content_div = soup.find(id="mw-content-text")
            if content_div:
                for link in content_div.find_all("a", href=True):
                    href = link["href"]
                    if href.startswith("/wiki/") and ":" not in href:
                        full_url = f"https://fr.wikipedia.org{href}"
                        if full_url not in links:
                            links.append(full_url)
                text_content = content_div.get_text(separator=" ", strip=True)
            return links, text_content
        except requests.exceptions.RequestException as e:
            self.supervisor.display_error(f"ERREUR réseau: {e}")
            return None