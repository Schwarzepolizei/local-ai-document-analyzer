def parse_txt(file_bytes: bytes) -> str:
    encodings = ["utf-8", "cp1251", "latin-1"]

    for encoding in encodings:
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue

    return file_bytes.decode("utf-8", errors="ignore")