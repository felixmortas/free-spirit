from bs4 import BeautifulSoup, Tag
import re

BLOCK_TAGS = {"p", "li", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6", "title"}

# Divs purement structurels/layout qu'on veut ignorer même s'ils ont du texte direct
STRUCTURAL_CLASSES = {
    "w-slider-mask", "w-slide", "w-slider-nav", "w-slider-dot",
    "w-slider-arrow-left", "w-slider-arrow-right", "w-embed",
}

class HtmlCleaner:
    def _normalize(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text.lower().strip())
    
    def _is_leaf_div(self, tag: Tag) -> bool:
        """
        Retourne True si le div contient du texte utile directement,
        sans enfants de type block-level (p, h1-h6, ul, etc.).
        Cela permet de capturer les divs "feuilles" comme <div class="price">$30</div>
        sans remonter leurs parents conteneurs.
        """
        BLOCK_CHILDREN = {"p", "div", "ul", "ol", "li", "table",
                          "h1", "h2", "h3", "h4", "h5", "h6", "section", "article"}
 
        # Ignorer les divs avec des classes purement structurelles
        classes = set(tag.get("class", []))
        if classes & STRUCTURAL_CLASSES:
            return False
 
        # Vérifier qu'aucun enfant n'est un élément block-level
        has_block_child = any(
            isinstance(child, Tag) and child.name in BLOCK_CHILDREN
            for child in tag.children
        )
        if has_block_child:
            return False
 
        # S'assurer qu'il y a du texte non-vide
        text = tag.get_text(" ", strip=True)
        return bool(text)

    def clean(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        
        # Supprimer les balises non pertinentes
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        seen = set()
        texts = []

        # Collecter les balises texte classiques + les divs feuilles
        candidates = soup.find_all(BLOCK_TAGS) + [
            tag for tag in soup.find_all("div")
            if self._is_leaf_div(tag)
        ]

        for tag in candidates:
            txt = tag.get_text(" ", strip=True)
            normalized = self._normalize(txt)
            if normalized and normalized not in seen:
                seen.add(normalized)
                texts.append(txt)

        return "\n".join(texts)