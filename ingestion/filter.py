from collections import Counter

class BoilerplateFilter:
    def __init__(self, threshold: float = 0.6):
        """Supprime les lignes présentes dans plus de `threshold` % des pages"""
        self.threshold = threshold

    def filter(self, pages: list[tuple[str, str]]) -> str:
        all_lines_per_page = []
        for _, text in pages:
            lines = {line.strip().lower() for line in text.splitlines() if line.strip()}
            all_lines_per_page.append(lines)

        # Compter dans combien de pages chaque ligne apparaît
        line_counts = Counter()
        for lines in all_lines_per_page:
            line_counts.update(lines)

        n_pages = len(pages)
        boilerplate = {
            line for line, count in line_counts.items()
            if count / n_pages >= self.threshold
        }

        # Reconstruire sans le boilerplate
        seen = set()
        unique_lines = []
        for _, text in pages:
            for line in text.splitlines():
                normalized = line.strip().lower()
                if normalized and normalized not in seen and normalized not in boilerplate:
                    seen.add(normalized)
                    unique_lines.append(line.strip())

        return "\n".join(unique_lines)