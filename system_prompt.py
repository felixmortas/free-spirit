def get_system_prompt(file_path="system_prompt.md"):
    """
    Loads the contents of a Markdown file and returns them as a string.

    Args:
        file_path (str): Path to the Markdown file to read. By default, “system_prompt.md”.

    Returns:
        str: The content of the Markdown file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {file_path} was not found.")
    except Exception as e:
        raise Exception(f"An error occurred while reading the file: {e}")