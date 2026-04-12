def get_system_prompt(file_path="system_prompt.md"):
    """
    Charge le contenu d'un fichier Markdown et le retourne sous forme de chaîne de caractères.

    Args:
        file_path (str): Chemin vers le fichier Markdown à lire. Par défaut, "system_prompt.md".

    Returns:
        str: Le contenu du fichier Markdown.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"Le fichier {file_path} n'a pas été trouvé.")
    except Exception as e:
        raise Exception(f"Une erreur est survenue lors de la lecture du fichier : {e}")