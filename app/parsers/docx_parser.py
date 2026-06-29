from io import BytesIO
from docx import Document
from docx.document import Document as DocumentObject
from docx.table import Table
from docx.text.paragraph import Paragraph


def iter_block_items(parent):
    if isinstance(parent, DocumentObject):
        parent_elm = parent.element.body
    else:
        parent_elm = parent._element

    for child in parent_elm.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, parent)
        elif child.tag.endswith("}tbl"):
            yield Table(child, parent)


def _clean_cell_text(text: str) -> str:
    return " ".join(text.split())


def _extract_table_rows(table: Table) -> list[dict]:
    rows = []

    for row in table.rows:
        cells = [_clean_cell_text(cell.text) for cell in row.cells]

        # защита от дублей merged cells
        compact_cells = []
        for cell in cells:
            if not compact_cells or compact_cells[-1] != cell:
                compact_cells.append(cell)

        if any(compact_cells):
            rows.append(
                {
                    "type": "table_row",
                    "text": " | ".join(compact_cells),
                    "cells": compact_cells,
                }
            )

    return rows


def parse_docx(file_bytes: bytes) -> dict:
    doc = Document(BytesIO(file_bytes))

    elements = []
    full_text_parts = []

    tables_count = 0
    equations_count = 0
    images_count = 0
    embedded_objects_count = 0

    raw_xml = doc.element.xml

    equations_count += raw_xml.count("<m:oMath")
    images_count += raw_xml.count("<pic:pic")
    embedded_objects_count += raw_xml.count("<o:OLEObject")

    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            text = block.text.strip()

            if not text:
                continue

            if "EMBED Equation" in text:
                equations_count += 1
                text = text.replace("EMBED Equation.3", "[FORMULA]")

            elements.append(
                {
                    "type": "paragraph",
                    "text": text,
                }
            )
            full_text_parts.append(text)

        elif isinstance(block, Table):
            tables_count += 1

            elements.append(
                {
                    "type": "table_start",
                    "text": f"[TABLE {tables_count}]",
                }
            )
            full_text_parts.append(f"[TABLE {tables_count}]")

            table_rows = _extract_table_rows(block)

            for row in table_rows:
                elements.append(row)
                full_text_parts.append(row["text"])

            elements.append(
                {
                    "type": "table_end",
                    "text": f"[/TABLE {tables_count}]",
                }
            )
            full_text_parts.append(f"[/TABLE {tables_count}]")

    return {
        "full_text": "\n\n".join(full_text_parts).strip(),
        "elements": elements,
        "stats": {
            "tables_count": tables_count,
            "equations_count": equations_count,
            "images_count": images_count,
            "embedded_objects_count": embedded_objects_count,
        },
    }