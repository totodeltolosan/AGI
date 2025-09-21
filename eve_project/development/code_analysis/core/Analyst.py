import re
from collections import Counter
from SupervisorInterface import SupervisorInterface  # Pour les type hints


class Analyst:
    """
    PHASE 2 - L'ANALYSTE : Module d'extraction de connaissances structurées

    Cette classe transforme le contenu brut des pages web en connaissances
    structurées et exploitables. Elle constitue le cerveau analytique du système.
    """

    def __init__(self, supervisor: SupervisorInterface):
        """TODO: Add docstring."""
        self.supervisor = supervisor

        # Liste des mots vides français pour l'extraction de mots-clés
        self.french_stop_words = {
            "le",
            "de",
            "et",
            "à",
            "un",
            "il",
            "être",
            "et",
            "en",
            "avoir",
            "que",
            "pour",
            "dans",
            "ce",
            "son",
            "une",
            "sur",
            "avec",
            "ne",
            "se",
            "pas",
            "tout",
            "plus",
            "par",
            "grand",
            "ce",
            "le",
            "premier",
            "vous",
            "ou",
            "son",
            "lui",
            "nous",
            "comme",
            "mais",
            "pouvoir",
            "dire",
            "elle",
            "prendre",
            "année",
            "bien",
            "aller",
            "y",
            "voir",
            "en",
            "faire",
            "plus",
            "aimer",
            "temps",
            "même",
            "si",
            "maintenant",
            "lui",
            "ou",
            "quand",
            "très",
            "me",
            "personne",
            "le",
            "avec",
            "tout",
            "faire",
            "son",
            "mettre",
            "autre",
            "on",
            "mais",
            "nous",
            "comme",
            "ou",
            "si",
            "leur",
            "bien",
            "être",
            "avoir",
            "vous",
            "ces",
            "me",
            "comme",
            "où",
            "ils",
            "peut",
            "cette",
            "la",
            "les",
            "des",
            "du",
            "aux",
            "au",
            "ces",
            "ses",
            "nos",
            "vos",
            "leurs",
            "cette",
            "celui",
            "celle",
            "ceux",
            "celles",
            "qui",
            "que",
            "quoi",
            "dont",
            "où",
            "est",
            "sont",
            "était",
            "étaient",
            "sera",
            "seront",
            "serait",
            "seraient",
            "été",
            "étant",
            "ayant",
            "eu",
            "eue",
            "eues",
            "eus",
            "eut",
            "eûmes",
            "eûtes",
            "eurent",
            "aussi",
            "encore",
            "déjà",
            "ici",
            "là",
            "alors",
            "ainsi",
            "donc",
            "cependant",
            "néanmoins",
            "toutefois",
            "pourtant",
            "car",
            "parce",
            "puisque",
            "comme",
            "si",
            "lorsque",
            "quand",
            "dès",
            "depuis",
            "jusqu",
            "pendant",
            "avant",
            "après",
        }

    def analyze(self, url: str, text_content: str, links: list) -> dict:
        """
        MÉTHODE PRINCIPALE D'ANALYSE

        Orchestre l'extraction complète des connaissances à partir du contenu brut.
        Retourne un dictionnaire structuré contenant toutes les analyses.
        """
        self.supervisor.display_info(f"🧠 ANALYSE COGNITIVE EN COURS pour: {url}")

        try:
            title = self._extract_title_from_url(url)
            summary = self._extract_summary(text_content)
            keywords = self._extract_keywords(text_content)
            definitions = self._find_definitions(text_content)
            related_concepts = self._filter_related_concepts(links)

            analysis_result = {
                "title": title,
                "summary": summary,
                "keywords": keywords,
                "definitions": definitions,
                "related_concepts": related_concepts,
            }

            self.supervisor.display_info(
                f"✅ ANALYSE TERMINÉE: {len(keywords)} mots-clés, {len(definitions)} définitions trouvées"
            )
            return analysis_result

        except Exception as e:
            self.supervisor.display_error(f"ERREUR lors de l'analyse de {url}: {e}")
            return {
                "title": "Erreur d'analyse",
                "summary": "L'analyse a échoué",
                "keywords": [],
                "definitions": {},
                "related_concepts": [],
            }

    def _extract_title_from_url(self, url: str) -> str:
        """Extrait le titre présumé à partir de l'URL Wikipedia"""
        try:
            if "/wiki/" in url:
                title = url.split("/wiki/")[-1]
                title = title.replace("_", " ")
                return title
            return "Titre non déterminé"
        except:
            return "Titre d'extraction échouée"

    def _extract_summary(self, text_content: str) -> str:
        """EXTRACTION DE RÉSUMÉ - Version V1: 300 premiers caractères significatifs"""
        if not text_content:
            return "Contenu vide"

        cleaned_text = " ".join(text_content.split())

        if len(cleaned_text) <= 300:
            return cleaned_text

        summary = cleaned_text[:300]
        last_period = summary.rfind(".")

        if last_period > 200:
            return summary[: last_period + 1]

        return summary + "..."

    def _extract_keywords(self, text_content: str) -> list:
        """EXTRACTION DE MOTS-CLÉS INTELLIGENTE"""
        if not text_content:
            return []

        normalized_text = re.sub(r"[^\w\s]", " ", text_content.lower())
        words = normalized_text.split()

        significant_words = [
            word
            for word in words
            if word not in self.french_stop_words and len(word) > 3 and word.isalpha()
        ]

        word_counts = Counter(significant_words)
        return [word for word, count in word_counts.most_common(10)]

    def _find_definitions(self, text_content: str) -> dict:
        """DÉTECTION DE DÉFINITIONS PAR HEURISTIQUE"""
        definitions = {}

        if not text_content:
            return definitions

        definition_patterns = [
            r"Le\s+([A-Z][a-zA-ZÀ-ÿ\s]+)\s+est\s+un[e]?\s+([^.]{10,200})\.",
            r"La\s+([A-Z][a-zA-ZÀ-ÿ\s]+)\s+est\s+un[e]?\s+([^.]{10,200})\.",
            r"Les\s+([A-Z][a-zA-ZÀ-ÿ\s]+)\s+sont\s+des\s+([^.]{10,200})\.",
            r"([A-Z][a-zA-ZÀ-ÿ\s]{3,30})\s+désigne\s+([^.]{10,200})\.",
            r"([A-Z][a-zA-ZÀ-ÿ\s]{3,30})\s+représente\s+([^.]{10,200})\.",
        ]

        for pattern in definition_patterns:
            matches = re.finditer(pattern, text_content)
            for match in matches:
                concept = match.group(1).strip()
                definition = match.group(2).strip()

                if len(concept) > 2 and len(definition) > 15:
                    definitions[concept] = definition

                if len(definitions) >= 10:
                    break

            if len(definitions) >= 10:
                break

        return definitions

    def _filter_related_concepts(self, links: list) -> list:
        """FILTRAGE DES CONCEPTS LIÉS PERTINENTS"""
        if not links:
            return []

        filtered_links = []
        excluded_keywords = [
            "discussion",
            "aide",
            "spécial",
            "utilisateur",
            "modèle",
            "catégorie",
            "fichier",
            "média",
            "projet",
            "portail",
        ]

        for link in links:
            if "fr.wikipedia.org/wiki/" in link:
                link_lower = link.lower()

                if not any(excluded in link_lower for excluded in excluded_keywords):
                    if ":" not in link.split("/wiki/")[-1]:
                        filtered_links.append(link)

                if len(filtered_links) >= 20:
                    break

        return filtered_links