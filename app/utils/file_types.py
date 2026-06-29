from pathlib import Path


def detect_file_type(file_name: str) -> str:
    ext = Path(file_name).suffix.lower()

    mapping = {
        ".txt": "txt",
        ".pdf": "pdf",
        ".doc": "doc",
        ".docx": "docx",
        ".xlsx": "xlsx",
        ".xls": "xlsx",
        ".jpg": "image",
        ".jpeg": "image",
        ".png": "image",
        ".rtf": "rtf",
    }

    return mapping.get(ext, "unknown")