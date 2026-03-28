from bs4 import BeautifulSoup
import re

BLOCK_TAGS = {"p", "li", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6", "title"}

class HtmlCleaner:
    def _normalize(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text.lower().strip())

    def clean(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        
        # Supprimer les balises non pertinentes
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        seen = set()
        texts = []

        for tag in soup.find_all(BLOCK_TAGS):
            txt = tag.get_text(" ", strip=True)
            normalized = self._normalize(txt)
            if normalized and normalized not in seen:
                seen.add(normalized)
                texts.append(txt)

        return "\n".join(texts)