from dataclasses import dataclass, field
from itertools import groupby

from app.schemas.document import Chunk, ETLResponse


@dataclass
class DocumentSection:
    title: str
    pages: list[int] = field(default_factory=list)
    chunks: list[Chunk] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n\n".join(chunk.text for chunk in self.chunks if chunk.text.strip())


class DocumentStructureBuilder:
    def __init__(self, fallback_chunk_group_size: int = 5) -> None:
        self.fallback_chunk_group_size = fallback_chunk_group_size

    def build(self, document: ETLResponse) -> list[DocumentSection]:
        chunks = document.content.chunks

        if not chunks:
            return []

        if self._has_section_titles(chunks):
            return self._group_by_section_title(chunks)

        if self._has_pages(chunks):
            return self._group_by_pages(chunks)

        return self._group_by_fixed_chunks(chunks)

    def _has_section_titles(self, chunks: list[Chunk]) -> bool:
        return any(chunk.section_title for chunk in chunks)

    def _has_pages(self, chunks: list[Chunk]) -> bool:
        return any(chunk.page_span for chunk in chunks)

    def _group_by_section_title(self, chunks: list[Chunk]) -> list[DocumentSection]:
        sections: list[DocumentSection] = []

        for section_title, group in groupby(
            chunks,
            key=lambda chunk: chunk.section_title or "Без раздела",
        ):
            grouped_chunks = list(group)

            sections.append(
                DocumentSection(
                    title=section_title,
                    pages=self._collect_pages(grouped_chunks),
                    chunks=grouped_chunks,
                )
            )

        return sections

    def _group_by_pages(self, chunks: list[Chunk]) -> list[DocumentSection]:
        sections: list[DocumentSection] = []

        for chunk in chunks:
            page_title = self._page_title(chunk)

            sections.append(
                DocumentSection(
                    title=page_title,
                    pages=chunk.page_span,
                    chunks=[chunk],
                )
            )

        return sections

    def _group_by_fixed_chunks(self, chunks: list[Chunk]) -> list[DocumentSection]:
        sections: list[DocumentSection] = []

        for index in range(0, len(chunks), self.fallback_chunk_group_size):
            grouped_chunks = chunks[index : index + self.fallback_chunk_group_size]
            section_number = index // self.fallback_chunk_group_size + 1

            sections.append(
                DocumentSection(
                    title=f"Фрагмент {section_number}",
                    pages=self._collect_pages(grouped_chunks),
                    chunks=grouped_chunks,
                )
            )

        return sections

    def _page_title(self, chunk: Chunk) -> str:
        if not chunk.page_span:
            return f"Фрагмент {chunk.chunk_order}"

        if len(chunk.page_span) == 1:
            return f"Страница {chunk.page_span[0]}"

        return f"Страницы {chunk.page_span[0]}–{chunk.page_span[-1]}"

    def _collect_pages(self, chunks: list[Chunk]) -> list[int]:
        pages: set[int] = set()

        for chunk in chunks:
            pages.update(chunk.page_span)

        return sorted(pages)