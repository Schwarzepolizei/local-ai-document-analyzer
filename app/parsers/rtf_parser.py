import re
from striprtf.striprtf import rtf_to_text


def _detect_rtf_encoding(text_preview: str) -> str:
    """
    Ищет codepage в заголовке RTF, например:
    \\ansicpg1251
    """
    match = re.search(r"\\ansicpg(\d+)", text_preview)
    if not match:
        return "cp1251"

    codepage = match.group(1)

    mapping = {
        "1251": "cp1251",
        "1252": "cp1252",
        "866": "cp866",
        "65001": "utf-8",
    }

    return mapping.get(codepage, "cp1251")


def _decode_rtf_bytes(file_bytes: bytes) -> str:
    """
    Аккуратно декодирует RTF как текст разметки, не теряя кириллицу.
    """
    preview_ascii = file_bytes[:4096].decode("ascii", errors="ignore")
    encoding = _detect_rtf_encoding(preview_ascii)

    try:
        return file_bytes.decode(encoding, errors="ignore")
    except Exception:
        pass

    for fallback in ("cp1251", "utf-8", "latin-1"):
        try:
            return file_bytes.decode(fallback, errors="ignore")
        except Exception:
            continue

    return file_bytes.decode("latin-1", errors="ignore")


def _restore_hex_escapes(rtf_text: str, encoding: str = "cp1251") -> str:
    """
    Преобразует RTF hex escapes вида \\'hh в соответствующие символы.
    Это помогает striprtf корректнее работать на русских RTF.
    """
    pattern = re.compile(r"\\'([0-9a-fA-F]{2})")

    def repl(match: re.Match) -> str:
        hex_value = match.group(1)
        try:
            return bytes.fromhex(hex_value).decode(encoding, errors="ignore")
        except Exception:
            return ""

    return pattern.sub(repl, rtf_text)


def parse_rtf(file_bytes: bytes) -> str:
    raw_rtf = _decode_rtf_bytes(file_bytes)

    preview_ascii = file_bytes[:4096].decode("ascii", errors="ignore")
    encoding = _detect_rtf_encoding(preview_ascii)

    prepared_rtf = _restore_hex_escapes(raw_rtf, encoding=encoding)

    text = rtf_to_text(prepared_rtf)
    return text.strip()