class SummaryResponseParser:
    markers = [
        "Ключевая мысль:",
        "Краткое саммари:",
        "Подробное саммари:",
        "Важные факты:",
    ]

    def extract_section(self, text: str, title: str) -> str:
        marker = f"{title}:"

        if marker not in text:
            return ""

        after = text.split(marker, 1)[1]

        for next_marker in self.markers:
            if next_marker != marker and next_marker in after:
                after = after.split(next_marker, 1)[0]

        return after.strip()

    def extract_list(self, text: str, title: str) -> list[str]:
        section = self.extract_section(text, title)

        items = []

        for line in section.splitlines():
            line = line.strip()

            if line.startswith("-"):
                items.append(line.removeprefix("-").strip())

        return items
