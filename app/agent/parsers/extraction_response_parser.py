from app.schemas.extraction import ExtractedItem


class ExtractionResponseParser:
    def parse_items(self, text: str) -> list[ExtractedItem]:
        found_section = self._extract_section(text, "Найдено")
        blocks = found_section.split("- Поле:")

        items: list[ExtractedItem] = []

        for block in blocks:
            block = block.strip()

            if not block:
                continue

            field = self._extract_value(block, "", ["Значение:", "Источник:", "Уверенность:"])
            value = self._extract_value(block, "Значение:", ["Источник:", "Уверенность:"])
            source = self._extract_value(block, "Источник:", ["Уверенность:"])
            confidence = self._extract_value(block, "Уверенность:", [])

            items.append(
                ExtractedItem(
                    field=field or "Неизвестное поле",
                    value=value or "",
                    source=source or None,
                    confidence=confidence or None,
                )
            )

        return items

    def parse_missing(self, text: str) -> list[str]:
        return self._extract_bullets(text, "Не найдено")

    def parse_notes(self, text: str) -> list[str]:
        return self._extract_bullets(text, "Примечания")

    def _extract_section(self, text: str, title: str) -> str:
        marker = f"{title}:"

        if marker not in text:
            return ""

        after = text.split(marker, 1)[1]

        next_markers = ["Найдено:", "Не найдено:", "Примечания:"]

        for next_marker in next_markers:
            if next_marker != marker and next_marker in after:
                after = after.split(next_marker, 1)[0]

        return after.strip()

    def _extract_bullets(self, text: str, title: str) -> list[str]:
        section = self._extract_section(text, title)
        result: list[str] = []

        for line in section.splitlines():
            line = line.strip()

            if line.startswith("-"):
                result.append(line.removeprefix("-").strip())

        return result

    def _extract_value(
        self,
        text: str,
        marker: str,
        stop_markers: list[str],
    ) -> str:
        if marker:
            if marker not in text:
                return ""

            value = text.split(marker, 1)[1]
        else:
            value = text

        for stop_marker in stop_markers:
            if stop_marker in value:
                value = value.split(stop_marker, 1)[0]

        return value.strip()