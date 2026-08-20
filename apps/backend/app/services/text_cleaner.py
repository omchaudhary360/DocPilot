import re


def clean_text(text: str, preserve_structure: bool = True) -> str:
    """
    Clean extracted text while preserving factual information.
    
    Removes:
    - Excessive whitespace
    - Common PDF artifacts
    - Extra blank lines
    
    Preserves:
    - Emails
    - Phone numbers
    - Dates
    - Currency symbols and amounts
    - Numbers and decimals
    - IDs and codes
    - Mathematical notation
    - Table separators (| and -)
    """
    
    if not text:
        return ""
    
    # Remove only specific problematic artifacts
    # DO NOT remove currency/special characters unnecessarily
    text = text.replace("ò", " ")
    text = text.replace("\u00ad", "")  # Soft hyphen
    
    # Normalize tabs and multiple spaces (but not all spaces)
    text = re.sub(r"[ \t]{2,}", " ", text)
    
    # Remove spaces around newlines
    text = re.sub(r" +\n +", "\n", text)
    text = re.sub(r"\n +", "\n", text)
    text = re.sub(r" +\n", "\n", text)
    
    # Remove excessive blank lines but keep single newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    # Clean each line individually
    lines = []
    for line in text.splitlines():
        # Remove leading/trailing spaces from each line
        cleaned_line = line.strip()
        if cleaned_line:
            lines.append(cleaned_line)
    
    # Rejoin
    text = "\n".join(lines)
    
    # Final trim
    text = text.strip()
    
    return text