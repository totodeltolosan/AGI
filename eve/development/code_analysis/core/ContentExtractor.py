"""
PROJET PROMETHEUS - MODULE SPÉCIALISÉ CONTENTEXTRACTOR (V1.0)

Mission: Agir comme un expert de l'analyse et de l'extraction de contenu
depuis des pages web HTML. Ce module est le "lecteur intelligent" du CodeHunter.

Responsabilités:
- Télécharger le contenu d'une URL.
- Extraire tous les snippets de code potentiels en utilisant plusieurs stratégies.
- Nettoyer, filtrer et attribuer un score de qualité à chaque snippet.
- Retourner une liste de candidats de code propres, prêts pour la validation.
"""

import re
from typing import List, Dict
import requests
from bs4 import BeautifulSoup


# --- CLASSE DE COULEURS PARTAGÉE ---
class Colors:
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


class ContentExtractor:
    """
    Spécialiste de l'extraction de snippets de code depuis des URLs.
    """

    def __init__(self, supervisor_interface):
        """
        Initialise l'extracteur de contenu.
        """
        self.supervisor = supervisor_interface
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Prometheus-ContentExtractor/1.0"})

        # Configuration
        self.min_code_lines = 2
        self.max_code_lines = 50

        print(
            f"{Colors.OKCYAN}[EXTRACTOR] - Module d'extraction de contenu initialisé.{Colors.ENDC}"
        )

    def extract_code_from_url(self, url: str, max_examples: int = 5) -> List[Dict]:
        """
        Méthode principale. Orchestre le téléchargement et l'extraction de code d'une URL.
        """
        try:
            self.supervisor.display_code_info(
                f"📄 Extraction intelligente depuis: {url}"
            )

            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            code_snippets = []

            # Stratégie 1: Code dans des sections d'exemples
            example_snippets = self._extract_example_sections(soup, url)
            code_snippets.extend(example_snippets)

            # Stratégie 2: Code dans les balises <pre><code>
            pre_snippets = self._extract_pre_code_blocks(soup, url)
            code_snippets.extend(pre_snippets)

            # Stratégie 3: Code interactif (sections avec highlight)
            interactive_snippets = self._extract_interactive_code(soup, url)
            code_snippets.extend(interactive_snippets)

            # Filtrage et scoring des snippets
            filtered_snippets = self._filter_and_score_snippets(code_snippets)

            self.supervisor.display_code_info(
                f"✅ {len(filtered_snippets)} exemples extraits et filtrés depuis {url}"
            )

            return filtered_snippets[:max_examples]

        except Exception as e:
            self.supervisor.display_error(
                f"Erreur lors de l'extraction de code depuis {url}: {e}"
            )
            return []

    def _extract_example_sections(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Extrait le code des sections explicitement marquées comme exemples."""
        snippets = []
        example_sections = soup.find_all(
            ["div", "section"], class_=re.compile(r"example|tutorial|demo", re.I)
        )
        for section in example_sections:
            pre_blocks = section.find_all("pre")
            for pre in pre_blocks:
                code_text = self._clean_code_text(pre.get_text())
                if self._is_valid_python_snippet(code_text):
                    snippets.append(
                        {"snippet": code_text, "url": url, "quality_score": 9}
                    )
        return snippets

    def _extract_pre_code_blocks(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Extraction classique des blocs <pre><code>."""
        snippets = []
        for pre in soup.find_all("pre"):
            if any(
                keyword in pre.get("class", [])
                for keyword in ["output", "result", "console"]
            ):
                continue
            code_text = self._clean_code_text(pre.get_text())
            if self._is_valid_python_snippet(code_text):
                snippets.append({"snippet": code_text, "url": url, "quality_score": 7})
        return snippets

    def _extract_interactive_code(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Extrait le code des éléments interactifs (highlight.js, etc.)."""
        snippets = []
        code_blocks = soup.find_all(
            ["code", "div"],
            class_=re.compile(r"highlight|language-python|python", re.I),
        )
        for block in code_blocks:
            if block.parent.name == "pre":
                continue
            code_text = self._clean_code_text(block.get_text())
            if self._is_valid_python_snippet(code_text):
                snippets.append({"snippet": code_text, "url": url, "quality_score": 8})
        return snippets

    def _clean_code_text(self, raw_text: str) -> str:
        """Nettoie le texte de code extrait."""
        if not raw_text:
            return ""
        lines = raw_text.split("\n")
        cleaned_lines = []
        for line in lines:
            line = re.sub(r"^\s*\d+[\s:\.>]+", "", line)
            line = re.sub(r"^>>>\s*", "", line)
            line = re.sub(r"^\.\.\.\s*", "", line)
            cleaned_lines.append(line)
        return "\n".join(cleaned_lines).strip()

    def _is_educational_code(self, code: str) -> bool:
        """Détermine si un code est pédagogique."""
        if not code or len(code.strip()) < 10:
            return False
        lines = code.strip().split("\n")
        if len(lines) < 2 or len(lines) > 20:
            return False

        educational_patterns = [
            r"print\s*\(",
            r"def\s+\w+\s*\([^)]*\):",
            r"for\s+\w+\s+in\s+",
            r"if\s+\w+\s*[=<>!]+",
            r"#.*example|#.*tutorial",
        ]
        educational_score = sum(
            1 for pattern in educational_patterns if re.search(pattern, code.lower())
        )

        complexity_penalties = [
            r"import\s+\w+\.\w+",
            r"class\s+\w+\([^)]+\)",
            r"try:\s*\n.*except",
            r"async\s+def",
        ]
        educational_score -= sum(
            2 for pattern in complexity_penalties if re.search(pattern, code, re.DOTALL)
        )

        return educational_score >= 1

    def _is_valid_python_snippet(self, code: str) -> bool:
        """Validation basique d'un snippet Python."""
        if not code or len(code.strip()) < 5:
            return False
        lines = code.strip().split("\n")
        if len(lines) < self.min_code_lines or len(lines) > self.max_code_lines:
            return False

        python_indicators = [
            "def ",
            "class ",
            "if ",
            "for ",
            "while ",
            "import ",
            "from ",
            "print(",
            "return",
            "and ",
            "or ",
            "not ",
            "in ",
            "is ",
            "=",
        ]
        return (
            sum(1 for indicator in python_indicators if indicator in code.lower()) >= 1
        )

    def _filter_and_score_snippets(self, snippets: List[Dict]) -> List[Dict]:
        """Filtre et score les snippets par qualité pédagogique."""
        if not snippets:
            return []

        for snippet in snippets:
            code = snippet["snippet"]
            base_score = snippet.get("quality_score", 5)
            if self._is_educational_code(code):
                base_score += 3
            if "#" in code and any(
                word in code.lower() for word in ["example", "demo", "simple"]
            ):
                base_score += 2
            line_count = len(code.split("\n"))
            if line_count < 3:
                base_score -= 2
            elif line_count > 15:
                base_score -= 1
            snippet["final_score"] = base_score

        filtered = sorted(snippets, key=lambda x: x.get("final_score", 0), reverse=True)

        unique_snippets, seen_codes = [], set()
        for snippet in filtered:
            code_signature = re.sub(r"\s+", " ", snippet["snippet"][:100]).strip()
            if code_signature not in seen_codes:
                seen_codes.add(code_signature)
                unique_snippets.append(snippet)
        return unique_snippets
