import re


def clean_text(text: str) -> str:
    """
    Clean text extracted from a PDF.
    """

    # Remove common PDF bullet/artifact characters
    text = text.replace("ò", " ")
    text = text.replace("•", " ")

    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)

    # Remove spaces around newlines
    text = re.sub(r" *\n *", "\n", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Clean each line
    lines = [line.strip() for line in text.splitlines()]

    # Remove empty lines at beginning/end
    text = "\n".join(lines).strip()

    return text