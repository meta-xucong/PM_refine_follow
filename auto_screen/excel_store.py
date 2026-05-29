from __future__ import annotations

import json
import zipfile
from html import escape
from pathlib import Path
from typing import Any


DEFAULT_SHEETS = ("alerts", "all_scored", "skipped", "cycles")


def col_name(index: int) -> str:
    name = ""
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        name = chr(65 + rem) + name
    return name


def cell_xml(row_idx: int, col_idx: int, value: Any) -> str:
    ref = f"{col_name(col_idx)}{row_idx}"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f'<c r="{ref}"><v>{value}</v></c>'
    text = escape("" if value is None else str(value))
    return f'<c r="{ref}" t="inlineStr"><is><t>{text}</t></is></c>'


def sheet_xml(rows: list[dict[str, Any]]) -> str:
    headers: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in headers:
                headers.append(key)
    if not headers:
        headers = ["empty"]
    all_rows = [dict(zip(headers, headers))] + rows
    body = []
    for ridx, row in enumerate(all_rows, start=1):
        cells = "".join(cell_xml(ridx, cidx, row.get(header)) for cidx, header in enumerate(headers))
        body.append(f'<row r="{ridx}">{cells}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"<sheetData>{''.join(body)}</sheetData>"
        "</worksheet>"
    )


class ExcelStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.sidecar = self.path.with_suffix(self.path.suffix + ".json")

    def load(self) -> dict[str, list[dict[str, Any]]]:
        if self.sidecar.exists():
            try:
                data = json.loads(self.sidecar.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError, TypeError):
                return {sheet: [] for sheet in DEFAULT_SHEETS}
            if not isinstance(data, dict):
                return {sheet: [] for sheet in DEFAULT_SHEETS}
            return {sheet: list(rows or []) for sheet, rows in data.items()}
        return {sheet: [] for sheet in DEFAULT_SHEETS}

    def append(self, sheet: str, row: dict[str, Any]) -> None:
        data = self.load()
        data.setdefault(sheet, []).append(row)
        self.save(data)

    def save(self, data: dict[str, list[dict[str, Any]]]) -> None:
        self.sidecar.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        sheet_names = list(data.keys()) or list(DEFAULT_SHEETS)
        with zipfile.ZipFile(self.path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("[Content_Types].xml", content_types_xml(len(sheet_names)))
            zf.writestr("_rels/.rels", package_rels_xml())
            zf.writestr("xl/workbook.xml", workbook_xml(sheet_names))
            zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml(len(sheet_names)))
            zf.writestr("xl/styles.xml", styles_xml())
            for idx, name in enumerate(sheet_names, start=1):
                zf.writestr(f"xl/worksheets/sheet{idx}.xml", sheet_xml(data.get(name, [])))


def content_types_xml(sheet_count: int) -> str:
    sheet_overrides = "".join(
        f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        for i in range(1, sheet_count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        f"{sheet_overrides}</Types>"
    )


def package_rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        "</Relationships>"
    )


def workbook_xml(sheet_names: list[str]) -> str:
    sheets = "".join(
        f'<sheet name="{escape(name[:31])}" sheetId="{idx}" r:id="rId{idx}"/>'
        for idx, name in enumerate(sheet_names, start=1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<sheets>{sheets}</sheets></workbook>"
    )


def workbook_rels_xml(sheet_count: int) -> str:
    rels = "".join(
        f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>'
        for i in range(1, sheet_count + 1)
    )
    rels += (
        f'<Relationship Id="rId{sheet_count + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f"{rels}</Relationships>"
    )


def styles_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="1"><fill><patternFill patternType="none"/></fill></fills>'
        '<borders count="1"><border/></borders>'
        '<cellStyleXfs count="1"><xf/></cellStyleXfs>'
        '<cellXfs count="1"><xf xfId="0"/></cellXfs>'
        "</styleSheet>"
    )
