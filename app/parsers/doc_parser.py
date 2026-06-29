import os
import subprocess
import tempfile

from app.parsers.docx_parser import parse_docx


def parse_doc(file_bytes: bytes) -> dict:
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "input.doc")

        with open(input_path, "wb") as f:
            f.write(file_bytes)

        result = subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                "docx",
                input_path,
                "--outdir",
                temp_dir,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"LibreOffice conversion failed: {result.stderr.strip()}"
            )

        output_path = os.path.join(temp_dir, "input.docx")

        if not os.path.exists(output_path):
            raise RuntimeError("Converted DOCX file was not created")

        with open(output_path, "rb") as f:
            converted_bytes = f.read()

        return parse_docx(converted_bytes)