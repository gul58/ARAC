"""Görev emri PDF çıktısı (reportlab)."""

from io import BytesIO

from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _register_fonts():
    """Türkçe karakter için sistem fontu dene; yoksa Helvetica."""
    candidates = [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVu"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuBold"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "DejaVu"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "DejaVuBold"),
    ]
    registered = {}
    for path, name in candidates:
        try:
            pdfmetrics.registerFont(TTFont(name, path))
            registered[name] = True
        except Exception:
            continue
    if "DejaVu" in registered and "DejaVuBold" not in registered:
        # Bold yoksa regular'ı bold adı olarak da kaydet
        try:
            pdfmetrics.registerFont(TTFont("DejaVuBold", candidates[0][0]))
        except Exception:
            pass
    return "DejaVu" if "DejaVu" in registered else "Helvetica"


def _fmt_dt(dt):
    if not dt:
        return ""
    local = timezone.localtime(dt)
    return local.strftime("%d.%m.%Y %H:%M")


def _fmt_km(value):
    if value is None:
        return ""
    if value == int(value):
        return str(int(value))
    return f"{value:.1f}".rstrip("0").rstrip(".")


def build_tasks_pdf(tasks, region_name=""):
    buffer = BytesIO()
    font = _register_fonts()
    bold = "DejaVuBold" if font == "DejaVu" else "Helvetica-Bold"

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleTR",
        parent=styles["Heading1"],
        fontName=bold,
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    org_style = ParagraphStyle(
        "OrgTR",
        parent=styles["Normal"],
        fontName=bold,
        fontSize=8,
        leading=11,
        alignment=TA_LEFT,
    )
    meta_style = ParagraphStyle(
        "MetaTR",
        parent=styles["Normal"],
        fontName=bold,
        fontSize=10,
        textColor=colors.HexColor("#c62828"),
        alignment=TA_CENTER,
    )
    normal = ParagraphStyle(
        "NormalTR",
        parent=styles["Normal"],
        fontName=font,
        fontSize=9,
        leading=12,
    )
    label = ParagraphStyle(
        "LabelTR",
        parent=styles["Normal"],
        fontName=bold,
        fontSize=8,
        leading=11,
    )
    section = ParagraphStyle(
        "SectionTR",
        parent=styles["Normal"],
        fontName=bold,
        fontSize=9,
        textColor=colors.white,
        alignment=TA_LEFT,
    )

    story = []
    header_bg = colors.HexColor("#1f4e79")
    label_bg = colors.HexColor("#eef3f8")

    for index, task in enumerate(tasks):
        if index > 0:
            story.append(Spacer(1, 8 * mm))
            # Sayfa sonu: her form ayrı sayfada
            from reportlab.platypus import PageBreak

            story.append(PageBreak())

        header = Table(
            [
                [
                    Paragraph(
                        "KOCAELİ BÜYÜKŞEHİR BELEDİYESİ<br/>YOL VE BAKIM DAİRESİ BAŞKANLIĞI",
                        org_style,
                    ),
                    Paragraph("KİRALIK ARAÇ GÖREV EMRİ", title_style),
                    Paragraph(
                        f"No: {task.display_number}<br/>Tarih: {timezone.localtime(task.departure_datetime).strftime('%d.%m.%Y')}",
                        meta_style,
                    ),
                ]
            ],
            colWidths=[55 * mm, 80 * mm, 45 * mm],
        )
        header.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOX", (2, 0), (2, 0), 1.5, colors.HexColor("#c62828")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(header)
        story.append(Spacer(1, 4 * mm))

        def section_table(title, rows):
            data = [[Paragraph(title, section)]]
            data.extend(
                [
                    [Paragraph(lbl, label), Paragraph(str(val or ""), normal)]
                    for lbl, val in rows
                ]
            )
            tbl = Table(data, colWidths=[60 * mm, 120 * mm])
            style_cmds = [
                ("BACKGROUND", (0, 0), (-1, 0), header_bg),
                ("SPAN", (0, 0), (-1, 0)),
                ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#9eb0c4")),
                ("BACKGROUND", (0, 1), (0, -1), label_bg),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
            tbl.setStyle(TableStyle(style_cmds))
            return tbl

        story.append(
            section_table(
                "GÖREVLENDİRİLEN BİRİM AMİRİNİN / ARACIN",
                [
                    ("ADI SOYADI", task.assigned_supervisor_name),
                    ("ÜNVANI", task.assigned_supervisor_title),
                    ("İMZASI", "Sistem Onaylı"),
                ],
            )
        )
        story.append(
            section_table(
                "ARACI SEVK EDEN AMİRİN",
                [
                    ("ADI / SOYADI", task.dispatching_supervisor_name),
                    ("ÜNVANI", task.dispatching_supervisor_title or "Formen"),
                    ("GÖREVİN TÜRÜ", task.task_type),
                    ("GİDECEĞİ YER", task.destination),
                    ("İMZASI", "Sistem Onaylı"),
                ],
            )
        )
        story.append(
            section_table(
                "ARAÇ / GÖREV BİLGİLERİ",
                [
                    ("AİT OLDUĞU KURULUŞ (FİRMA)", task.company.name),
                    (
                        "ARACIN PLAKASI VE CİNSİ",
                        f"{task.vehicle.plate} - {task.vehicle.vehicle_type}",
                    ),
                    (
                        "SÜRÜCÜNÜN ADI/SOYADI",
                        f"{task.driver.full_name} ({task.driver.duty})",
                    ),
                    ("İLK KM", _fmt_km(task.start_km)),
                    ("SON KM", _fmt_km(task.end_km)),
                    ("YOL (KM)", task.distance_display if task.distance_km is not None else ""),
                    ("ÇIKIŞ", _fmt_dt(task.departure_datetime)),
                    ("GİRİŞ", _fmt_dt(task.arrival_datetime)),
                    ("SÜRE", task.duration_display),
                    ("BÖLGE", task.region.name if task.region_id else region_name),
                ],
            )
        )
        story.append(Spacer(1, 4 * mm))
        notes = Paragraph(
            "1) Bu görev emri üç nüsha olarak düzenlenir.<br/>"
            "2) Denetim yetkililerine talep halinde ibraz edilir.<br/>"
            "3) Sürücü görev süresince trafik kurallarına uyar.",
            normal,
        )
        story.append(notes)

    if not tasks:
        story.append(Paragraph("Seçilen tarih aralığında görev emri bulunamadı.", normal))

    doc.build(story)
    buffer.seek(0)
    return buffer
