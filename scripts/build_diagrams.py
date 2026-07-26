# -*- coding: utf-8 -*-
"""Build draw.io-style SVG diagrams + editable .drawio XML for FACT playbook."""
from __future__ import annotations

import html
import uuid
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parents[1] / "diagrams"

# role fills
C = {
    "fin": ("#FFF0F0", "#C00000"),
    "pm": ("#F5F5F5", "#1A1A1A"),
    "exec": ("#EEF6F6", "#0F6B6B"),
    "dec": ("#FFF7ED", "#B45309"),
    "in": ("#F3F1EF", "#666666"),
    "ok": ("#ECFDF5", "#166534"),
    "qa": ("#F8FAFC", "#334155"),
    "acc": ("#F5F5F5", "#444444"),
}


def legend_svg(y: int = 8) -> str:
    items = [
        (8, "fin", "Финансы"),
        (110, "pm", "ПМ / ТД"),
        (210, "exec", "Исполнители"),
        (340, "dec", "Решение"),
        (440, "in", "Клиент / вход"),
        (580, "ok", "Закрытие"),
    ]
    parts = []
    for x, key, label in items:
        fill, stroke = C[key]
        parts.append(
            f'<rect x="{x}" y="{y}" width="14" height="14" rx="2" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
            f'<text x="{x + 20}" y="{y + 12}" class="leg">{label}</text>'
        )
    return "\n  ".join(parts)


def styles() -> str:
    return """
  <style>
    .t { font: 600 13px Onest, system-ui, sans-serif; fill: #1A1A1A; }
    .s { font: 400 11px Onest, system-ui, sans-serif; fill: #555555; }
    .leg { font: 600 12px Onest, system-ui, sans-serif; fill: #333333; }
    .edge { stroke: #8A0000; stroke-width: 1.75; fill: none; }
    .arr { fill: #8A0000; }
    .lab { font: 600 11px Onest, system-ui, sans-serif; fill: #8A0000; }
    .phase { font: 700 12px Unbounded, Onest, system-ui, sans-serif; fill: #C00000; letter-spacing: 0.04em; }
    .frame { fill: #FAFAFA; stroke: #E8E4E1; stroke-width: 1; }
  </style>
"""


def node(x, y, w, h, title, sub, role: str) -> str:
    fill, stroke = C[role]
    tid = html.escape(title)
    sid = html.escape(sub)
    cy = y + h / 2
    if sub:
        return (
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1.75"/>'
            f'<text x="{x + w/2}" y="{cy - 6}" text-anchor="middle" class="t">{tid}</text>'
            f'<text x="{x + w/2}" y="{cy + 12}" text-anchor="middle" class="s">{sid}</text>'
        )
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1.75"/>'
        f'<text x="{x + w/2}" y="{cy + 5}" text-anchor="middle" class="t">{tid}</text>'
    )


def diamond(cx, cy, w, h, title, role="dec") -> str:
    fill, stroke = C[role]
    half_w, half_h = w / 2, h / 2
    pts = f"{cx},{cy - half_h} {cx + half_w},{cy} {cx},{cy + half_h} {cx - half_w},{cy}"
    return (
        f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1.75"/>'
        f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" class="t">{html.escape(title)}</text>'
    )


def arrow_down(x1, y1, x2, y2, label: str | None = None) -> str:
    # line + triangle
    parts = [
        f'<path d="M{x1} {y1} L{x2} {y2 - 6}" class="edge" marker-end="url(#arrow)"/>'
    ]
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        # label on side of line to avoid overlap
        parts.append(
            f'<rect x="{mx + 8}" y="{my - 10}" width="{8 + len(label) * 7}" height="18" rx="2" fill="#fff" stroke="#E8E4E1"/>'
            f'<text x="{mx + 14}" y="{my + 3}" class="lab">{html.escape(label)}</text>'
        )
    return "\n  ".join(parts)


def arrow_line(x1, y1, x2, y2, label: str | None = None, label_side: str = "right") -> str:
    parts = [f'<path d="M{x1} {y1} L{x2} {y2}" class="edge" marker-end="url(#arrow)"/>']
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if label_side == "left":
            tx = mx - 10 - len(label) * 7
            parts.append(
                f'<rect x="{tx - 6}" y="{my - 10}" width="{12 + len(label) * 7}" height="18" rx="2" fill="#fff" stroke="#E8E4E1"/>'
                f'<text x="{tx}" y="{my + 3}" class="lab">{html.escape(label)}</text>'
            )
        else:
            parts.append(
                f'<rect x="{mx + 8}" y="{my - 10}" width="{12 + len(label) * 7}" height="18" rx="2" fill="#fff" stroke="#E8E4E1"/>'
                f'<text x="{mx + 14}" y="{my + 3}" class="lab">{html.escape(label)}</text>'
            )
    return "\n  ".join(parts)


def defs() -> str:
    return """
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" class="arr"/>
    </marker>
  </defs>
"""


def wrap(view_w: int, view_h: int, body: str, title: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {view_h}" role="img" aria-label="{html.escape(title)}">
{styles()}
{defs()}
  {legend_svg(10)}
  <line x1="24" y1="40" x2="{view_w - 24}" y2="40" stroke="#E8E4E1" stroke-width="1"/>
  {body}
</svg>
"""


def build_01_annual() -> str:
    # horizontal chain centered
    w, h = 160, 58
    gap = 36
    start_x = 40
    y = 90
    roles = [
        ("in", "Инициатор", "ПМ / ТД / HR / рук."),
        ("acc", "Согласующий", "Аккаунт / ОД / ГД"),
        ("fin", "Финансы", "заявка → Epic"),
        ("pm", "ПМ", "Story / Subtask"),
        ("exec", "Исполнители", "Log Work"),
    ]
    parts = ['<text x="360" y="68" text-anchor="middle" class="phase">ГОДОВОЙ ЗАПУСК EPIC</text>']
    xs = []
    for i, (role, t, s) in enumerate(roles):
        x = start_x + i * (w + gap)
        xs.append(x)
        parts.append(node(x, y, w, h, t, s, role))
        if i:
            x1 = xs[i - 1] + w
            x2 = x
            mid_y = y + h / 2
            parts.append(arrow_line(x1, mid_y, x2 - 2, mid_y))
    # tree note under last
    parts.append(
        '<text x="360" y="190" text-anchor="middle" class="s">'
        "Тип Epic зависит от контура: Оценка · Сервис · Собеседования · Downtime / Meeting"
        "</text>"
    )
    return wrap(920, 220, "\n  ".join(parts), "Универсальный запуск годового Epic")


def build_02_fixed() -> str:
    parts = []
    # two phase frames
    parts.append('<rect class="frame" x="24" y="56" width="360" height="320" rx="6"/>')
    parts.append('<rect class="frame" x="420" y="56" width="360" height="320" rx="6"/>')
    parts.append('<text x="204" y="78" text-anchor="middle" class="phase">ФАЗА ОЦЕНКИ</text>')
    parts.append('<text x="600" y="78" text-anchor="middle" class="phase">ФАЗА РЕАЛИЗАЦИИ</text>')

    # left column
    lw, lh = 220, 48
    lx = 94
    left = [
        ("pm", "Story в Epic (Оценка)", "ПМ / ТД"),
        ("pm", "Subtask исполнителям", "ПМ / ТД"),
        ("exec", "Списание часов", "Исполнители"),
        ("acc", "Согласование оценки", "Аккаунт / ОД"),
    ]
    for i, (role, t, s) in enumerate(left):
        y = 100 + i * 64
        parts.append(node(lx, y, lw, lh, t, s, role))
        if i:
            parts.append(arrow_line(lx + lw / 2, y - 16, lx + lw / 2, y - 2))

    # right column
    rx = 490
    right = [
        ("in", "Клиент даёт старт", "вход"),
        ("fin", "Epic (Реализация)", "Финансы"),
        ("pm", "Перенос Story + Subtask", "ПМ"),
        ("exec", "Факт часов", "Исполнители"),
        ("ok", "Приёмка · закрытие · акты", "Клиент / Финансы"),
    ]
    for i, (role, t, s) in enumerate(right):
        y = 96 + i * 52
        parts.append(node(rx, y, lw, lh if i < 4 else 52, t, s, role))
        if i:
            parts.append(arrow_line(rx + lw / 2, y - 12, rx + lw / 2, y - 2))

    # bridge from left to right
    parts.append(arrow_line(314, 340, 490, 120, "старт работ", "right"))
    return wrap(804, 400, "\n  ".join(parts), "Фикс. бюджет: оценка → реализация")


def build_03_estimation() -> str:
    # tree: finance root -> pm story -> pm subtask -> fork to exec + reports
    parts = ['<text x="400" y="64" text-anchor="middle" class="phase">ДЕРЕВО СОЗДАНИЯ АРТЕФАКТОВ</text>']
    w, h = 260, 56
    cx = 400
    # root
    parts.append(node(cx - w / 2, 84, w, h, "Финансы", "Epic (Оценка) + плановые часы", "fin"))
    parts.append(arrow_line(cx, 140, cx, 158))
    parts.append(node(cx - w / 2, 160, w, h, "ПМ / ТД", "Story оценки → к Epic", "pm"))
    parts.append(arrow_line(cx, 216, cx, 234))
    parts.append(node(cx - w / 2, 236, w, h, "ПМ / ТД", "Subtask типа «Оценка»", "pm"))

    # fork: stem → T-junction → two leaves
    left_x, right_x = 160, 540
    mid_y = 318
    parts.append(f'<path d="M{cx} 292 V{mid_y}" class="edge"/>')
    parts.append(f'<path d="M{left_x + w/2} {mid_y} H{right_x + w/2}" class="edge"/>')
    parts.append(
        f'<path d="M{left_x + w/2} {mid_y} V336" class="edge" marker-end="url(#arrow)"/>'
    )
    parts.append(
        f'<path d="M{right_x + w/2} {mid_y} V336" class="edge" marker-end="url(#arrow)"/>'
    )

    parts.append(node(left_x, 340, w, h, "Исполнители", "Log Work в Subtask", "exec"))
    parts.append(node(right_x, 340, w, h, "Отчёты", "план/факт по Epic", "ok"))
    return wrap(800, 430, "\n  ".join(parts), "Цепочка оценки")


def build_04_sla() -> str:
    parts = ['<text x="400" y="64" text-anchor="middle" class="phase">SLA · ДЕРЕВО РЕШЕНИЙ</text>']
    w, h = 220, 50
    cx = 400

    parts.append(node(cx - w / 2, 80, w, h, "Обращение клиента", "вход", "in"))
    parts.append(arrow_line(cx, 130, cx, 148))
    parts.append(node(cx - w / 2, 150, w, h, "1-я линия", "Issue в Service Desk", "pm"))
    parts.append(arrow_line(cx, 200, cx, 218))

    # decision 1
    parts.append(diamond(cx, 250, 200, 56, "Консультация?"))
    # yes left / no right - labels beside edges
    ly, ry = 200, 520
    parts.append(f'<path d="M{cx - 100} 250 L{ly + w/2} 250" class="edge"/>')
    parts.append(f'<path d="M{cx + 100} 250 L{ry + w/2} 250" class="edge"/>')
    parts.append('<text x="250" y="242" class="lab">Да</text>')
    parts.append('<text x="530" y="242" class="lab">Нет</text>')
    parts.append(arrow_line(ly + w / 2, 250, ly + w / 2, 278))
    parts.append(arrow_line(ry + w / 2, 250, ry + w / 2, 278))

    parts.append(node(ly, 280, w, h, "Ответ + Log Work", "в Issue", "ok"))
    parts.append(node(ry, 280, w, h, "Issue в Epic Сервис", "эскалация", "fin"))

    parts.append(arrow_line(ry + w / 2, 330, ry + w / 2, 348))
    parts.append(diamond(ry + w / 2, 380, 180, 52, "Тип работ?"))

    qax, pmx = 360, 580
    parts.append(f'<path d="M{ry + w/2 - 90} 380 L{qax + 90} 380" class="edge"/>')
    parts.append(f'<path d="M{ry + w/2 + 90} 380 L{pmx + 90} 380" class="edge"/>')
    # fix diamond center for right branch - diamond at ry+w/2 = 520+110 = wait
    # ry = 520, w = 220, center = 630. Recalculate layout more carefully.

    return None  # will rewrite cleanly below


def build_04_sla_v2() -> str:
    """Cleaner SLA tree, fully centered."""
    parts = ['<text x="420" y="64" text-anchor="middle" class="phase">SLA · ДЕРЕВО РЕШЕНИЙ</text>']
    w, h = 200, 48
    root = 420

    parts.append(node(root - w / 2, 80, w, h, "Обращение клиента", "вход", "in"))
    parts.append(arrow_line(root, 128, root, 146))
    parts.append(node(root - w / 2, 148, w, h, "1-я линия", "Issue в Service Desk", "pm"))
    parts.append(arrow_line(root, 196, root, 214))
    parts.append(diamond(root, 248, 190, 54, "Консультация?"))

    left_c, right_c = 220, 620
    # elbows from diamond
    parts.append(f'<path d="M{root - 95} 248 H{left_c}" class="edge"/>')
    parts.append(f'<path d="M{root + 95} 248 H{right_c}" class="edge"/>')
    parts.append(f'<path d="M{left_c} 248 V{278}" class="edge" marker-end="url(#arrow)"/>')
    parts.append(f'<path d="M{right_c} 248 V{278}" class="edge" marker-end="url(#arrow)"/>')
    parts.append('<text x="290" y="240" class="lab">Да</text>')
    parts.append('<text x="530" y="240" class="lab">Нет</text>')

    parts.append(node(left_c - w / 2, 282, w, h, "Ответ + Log Work", "в Issue", "ok"))
    parts.append(node(right_c - w / 2, 282, w, h, "Issue в Epic Сервис", "эскалация", "fin"))

    parts.append(arrow_line(right_c, 330, right_c, 348))
    parts.append(diamond(right_c, 380, 170, 50, "Тип?"))

    qa_c, pm_c = 480, 760
    parts.append(f'<path d="M{right_c - 85} 380 H{qa_c}" class="edge"/>')
    parts.append(f'<path d="M{right_c + 85} 380 H{pm_c}" class="edge"/>')
    parts.append(f'<path d="M{qa_c} 380 V{410}" class="edge" marker-end="url(#arrow)"/>')
    parts.append(f'<path d="M{pm_c} 380 V{410}" class="edge" marker-end="url(#arrow)"/>')
    parts.append('<text x="545" y="372" class="lab">Ошибка</text>')
    parts.append('<text x="680" y="372" class="lab">Доработка</text>')

    parts.append(node(qa_c - w / 2, 414, w, h, "Назначение на QA", "качество", "qa"))
    parts.append(node(pm_c - w / 2, 414, w, h, "ПМ / разработка", "доработка", "pm"))

    # merge to bottom
    merge_y = 500
    parts.append(f'<path d="M{qa_c} 462 V{merge_y}" class="edge"/>')
    parts.append(f'<path d="M{pm_c} 462 V{merge_y}" class="edge"/>')
    parts.append(f'<path d="M{qa_c} {merge_y} H{pm_c}" class="edge"/>')
    mid = (qa_c + pm_c) / 2
    parts.append(f'<path d="M{mid} {merge_y} V{merge_y + 18}" class="edge" marker-end="url(#arrow)"/>')
    parts.append(node(mid - w / 2, merge_y + 22, w, h, "Subtask + списание", "исполнители", "exec"))

    return wrap(880, 590, "\n  ".join(parts), "SLA: консультация или эскалация")


def cell(cid: str, parent: str, value: str, x: int, y: int, w: int, h: int, style: str) -> str:
    return (
        f'<mxCell id="{cid}" value="{escape(value)}" style="{style}" vertex="1" parent="{parent}">'
        f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'
    )


def edge(cid: str, parent: str, source: str, target: str, label: str = "") -> str:
    style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#8A0000;fontColor=#8A0000;"
    return (
        f'<mxCell id="{cid}" value="{escape(label)}" style="{style}" edge="1" parent="{parent}" source="{source}" target="{target}">'
        f'<mxGeometry relative="1" as="geometry"/></mxCell>'
    )


def drawio_file(name: str, cells: str, page_w=900, page_h=600) -> str:
    did = uuid.uuid4().hex[:8]
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2026-07-26T00:00:00.000Z" agent="FACT" version="22.0.0">
  <diagram id="{did}" name="{escape(name)}">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{page_w}" pageHeight="{page_h}" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        {cells}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""


STYLE = {
    "fin": "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF0F0;strokeColor=#C00000;fontStyle=1;fontSize=12;",
    "pm": "rounded=1;whiteSpace=wrap;html=1;fillColor=#F5F5F5;strokeColor=#1A1A1A;fontStyle=1;fontSize=12;",
    "exec": "rounded=1;whiteSpace=wrap;html=1;fillColor=#EEF6F6;strokeColor=#0F6B6B;fontStyle=1;fontSize=12;",
    "dec": "rhombus;whiteSpace=wrap;html=1;fillColor=#FFF7ED;strokeColor=#B45309;fontStyle=1;fontSize=12;",
    "in": "rounded=1;whiteSpace=wrap;html=1;fillColor=#F3F1EF;strokeColor=#666666;fontStyle=1;fontSize=12;",
    "ok": "rounded=1;whiteSpace=wrap;html=1;fillColor=#ECFDF5;strokeColor=#166534;fontStyle=1;fontSize=12;",
    "qa": "rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#334155;fontStyle=1;fontSize=12;",
}


def build_drawio_estimation() -> str:
    cells = []
    cells.append(cell("n1", "1", "Финансы\\nEpic (Оценка) + плановые часы", 300, 40, 240, 60, STYLE["fin"]))
    cells.append(cell("n2", "1", "ПМ / ТД\\nStory оценки → к Epic", 300, 140, 240, 60, STYLE["pm"]))
    cells.append(cell("n3", "1", "ПМ / ТД\\nSubtask типа «Оценка»", 300, 240, 240, 60, STYLE["pm"]))
    cells.append(cell("n4", "1", "Исполнители\\nLog Work в Subtask", 120, 360, 220, 60, STYLE["exec"]))
    cells.append(cell("n5", "1", "Отчёты\\nплан/факт по Epic", 500, 360, 220, 60, STYLE["ok"]))
    cells.append(edge("e1", "1", "n1", "n2"))
    cells.append(edge("e2", "1", "n2", "n3"))
    cells.append(edge("e3", "1", "n3", "n4"))
    cells.append(edge("e4", "1", "n3", "n5"))
    return drawio_file("Цепочка оценки", "\n        ".join(cells), 840, 500)


def build_drawio_annual() -> str:
    cells = []
    items = [
        ("a1", 40, "Инициатор\\nПМ / ТД / HR", "in"),
        ("a2", 220, "Согласующий\\nАккаунт / ОД / ГД", "pm"),
        ("a3", 400, "Финансы\\nEpic", "fin"),
        ("a4", 580, "ПМ\\nStory / Subtask", "pm"),
        ("a5", 760, "Исполнители\\nLog Work", "exec"),
    ]
    for cid, x, val, role in items:
        cells.append(cell(cid, "1", val, x, 120, 160, 60, STYLE[role]))
    for i in range(4):
        cells.append(edge(f"ae{i}", "1", items[i][0], items[i + 1][0]))
    return drawio_file("Годовой Epic", "\n        ".join(cells), 980, 320)


def build_drawio_fixed() -> str:
    cells = []
    left = [
        ("f1", "Story в Epic (Оценка)", "pm"),
        ("f2", "Subtask исполнителям", "pm"),
        ("f3", "Списание часов", "exec"),
        ("f4", "Согласование оценки", "pm"),
    ]
    for i, (cid, val, role) in enumerate(left):
        cells.append(cell(cid, "1", val, 80, 40 + i * 80, 220, 55, STYLE[role]))
        if i:
            cells.append(edge(f"fl{i}", "1", left[i - 1][0], cid))
    right = [
        ("r1", "Клиент: старт", "in"),
        ("r2", "Epic (Реализация)", "fin"),
        ("r3", "Перенос Story + Subtask", "pm"),
        ("r4", "Факт часов", "exec"),
        ("r5", "Приёмка · акты", "ok"),
    ]
    for i, (cid, val, role) in enumerate(right):
        cells.append(cell(cid, "1", val, 420, 20 + i * 70, 220, 55, STYLE[role]))
        if i:
            cells.append(edge(f"fr{i}", "1", right[i - 1][0], cid))
    cells.append(edge("bridge", "1", "f4", "r1", "старт"))
    return drawio_file("Фикс. бюджет", "\n        ".join(cells), 720, 420)


def build_drawio_sla() -> str:
    cells = [
        cell("s1", "1", "Обращение клиента", 320, 20, 200, 50, STYLE["in"]),
        cell("s2", "1", "1-я линия\\nIssue в SD", 320, 100, 200, 50, STYLE["pm"]),
        cell("s3", "1", "Консультация?", 330, 180, 180, 70, STYLE["dec"]),
        cell("s4", "1", "Ответ + Log Work", 80, 290, 200, 50, STYLE["ok"]),
        cell("s5", "1", "Issue в Epic Сервис", 480, 290, 200, 50, STYLE["fin"]),
        cell("s6", "1", "Тип?", 500, 380, 160, 60, STYLE["dec"]),
        cell("s7", "1", "QA", 360, 480, 160, 50, STYLE["qa"]),
        cell("s8", "1", "ПМ / разработка", 600, 480, 180, 50, STYLE["pm"]),
        cell("s9", "1", "Subtask + списание", 460, 580, 200, 50, STYLE["exec"]),
        edge("se1", "1", "s1", "s2"),
        edge("se2", "1", "s2", "s3"),
        edge("se3", "1", "s3", "s4", "Да"),
        edge("se4", "1", "s3", "s5", "Нет"),
        edge("se5", "1", "s5", "s6"),
        edge("se6", "1", "s6", "s7", "Ошибка"),
        edge("se7", "1", "s6", "s8", "Доработка"),
        edge("se8", "1", "s7", "s9"),
        edge("se9", "1", "s8", "s9"),
    ]
    return drawio_file("SLA", "\n        ".join(cells), 860, 700)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    svgs = {
        "01-annual.svg": build_01_annual(),
        "02-fixed-budget.svg": build_02_fixed(),
        "03-estimation.svg": build_03_estimation(),
        "04-sla.svg": build_04_sla_v2(),
    }
    for name, content in svgs.items():
        (OUT / name).write_text(content, encoding="utf-8")
        print("svg", name)

    drawios = {
        "01-annual.drawio": build_drawio_annual(),
        "02-fixed-budget.drawio": build_drawio_fixed(),
        "03-estimation.drawio": build_drawio_estimation(),
        "04-sla.drawio": build_drawio_sla(),
    }
    for name, content in drawios.items():
        (OUT / name).write_text(content, encoding="utf-8")
        print("drawio", name)


if __name__ == "__main__":
    main()
