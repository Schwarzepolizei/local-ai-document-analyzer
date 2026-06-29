import re


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fix_hyphenation(text: str) -> str:
    """
    Склеивает переносы слов вида:
    доку-
    мент -> документ
    """
    return re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)


def fix_single_newlines(text: str) -> str:
    """
    Склеивает одиночные переводы строк внутри абзаца,
    но сохраняет пустые строки между абзацами.
    """
    lines = text.split("\n")
    result = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        if not stripped:
            result.append("")
            continue

        if result and result[-1] != "":
            prev = result[-1]

            if not prev.endswith((".", "!", "?", ":", ";")):
                result[-1] = prev + " " + stripped
            else:
                result.append(stripped)
        else:
            result.append(stripped)

    return "\n".join(result)


def clean_text(text: str) -> str:
    text = normalize_whitespace(text)
    text = fix_hyphenation(text)
    text = fix_single_newlines(text)
    text = normalize_whitespace(text)
    return text