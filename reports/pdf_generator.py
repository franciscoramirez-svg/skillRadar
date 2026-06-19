import io
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from core.risk import NivelRiesgo

COLOR_BAJO = colors.HexColor("#4CAF50")
COLOR_MODERADO = colors.HexColor("#FF9800")
COLOR_ALTO = colors.HexColor("#F44336")
COLOR_CRITICO = colors.HexColor("#9C27B0")

COLOR_MAP = {
    NivelRiesgo.BAJO.value: COLOR_BAJO,
    NivelRiesgo.MODERADO.value: COLOR_MODERADO,
    NivelRiesgo.ALTO.value: COLOR_ALTO,
    NivelRiesgo.CRITICO.value: COLOR_CRITICO,
}


class PDFReporte:
    def __init__(self, titulo: str = "SkillRadar - Reporte de Rendimiento"):
        self.titulo = titulo
        self.buf = io.BytesIO()
        self.doc = SimpleDocTemplate(
            self.buf,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )
        self.styles = getSampleStyleSheet()
        self._crear_estilos()
        self.elementos = []

    def _crear_estilos(self):
        self.styles.add(ParagraphStyle(
            "TituloPrincipal",
            parent=self.styles["Title"],
            fontSize=22,
            textColor=colors.HexColor("#1a1a2e"),
            spaceAfter=6,
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            "Subtitulo",
            parent=self.styles["Normal"],
            fontSize=12,
            textColor=colors.HexColor("#666666"),
            spaceAfter=4,
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            "EncabezadoSeccion",
            parent=self.styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#1a1a2e"),
            spaceBefore=12,
            spaceAfter=6,
            borderWidth=0,
            borderColor=colors.HexColor("#2196F3"),
            borderPadding=4,
        ))
        self.styles.add(ParagraphStyle(
            "CeldaTabla",
            parent=self.styles["Normal"],
            fontSize=8,
            textColor=colors.white,
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            "TextoClinico",
            parent=self.styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#333333"),
            spaceAfter=4,
            alignment=TA_LEFT,
        ))

    def agregar_encabezado(self, fecha: str, temperatura: str, wbgt: str):
        self.elementos.append(Paragraph("SkillRadar", self.styles["TituloPrincipal"]))
        self.elementos.append(Paragraph(
            "Sistema de Analítica Deportiva y Prevención Térmica",
            self.styles["Subtitulo"],
        ))
        self.elementos.append(Spacer(1, 6))

        info = (
            f"<b>Fecha:</b> {fecha} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Temperatura:</b> {temperatura} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>WBGT:</b> {wbgt}"
        )
        self.elementos.append(Paragraph(info, self.styles["Subtitulo"]))
        self.elementos.append(Spacer(1, 12))

    def agregar_tabla_plantilla(self, df_procesado):
        self.elementos.append(Paragraph("Plantilla General", self.styles["EncabezadoSeccion"]))

        data = [["#", "Jugador", "Posición", "Distrib.", "Ataque", "Defensa", "Km", "Rend."]]
        for idx, (_, row) in enumerate(df_procesado.iterrows(), 1):
            color = COLOR_BAJO
            rend = row["Rendimiento"]
            if rend >= 70:
                color = colors.HexColor("#4CAF50")
            elif rend >= 50:
                color = colors.HexColor("#FF9800")
            else:
                color = colors.HexColor("#F44336")

            data.append([
                str(idx),
                row["Nombre_Jugador"],
                row["Posicion"],
                f"{row['Distribucion']:.0f}",
                f"{row['Ataque']:.0f}",
                f"{row['Defensa']:.0f}",
                f"{row['Km_Puntaje']:.0f}",
                Paragraph(f"{row['Rendimiento']:.0f}", ParagraphStyle(
                    "rend", parent=self.styles["CeldaTabla"],
                    textColor=color, fontSize=9, fontName="Helvetica-Bold",
                    alignment=TA_CENTER,
                )),
            ])

        col_widths = [20, 90, 55, 50, 50, 50, 50, 45]
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ]))
        self.elementos.append(t)
        self.elementos.append(Spacer(1, 12))

    def agregar_radares(self, radares: list[tuple[str, io.BytesIO]]):
        self.elementos.append(PageBreak())
        self.elementos.append(Paragraph("Fichas Individuales - SkillRadar", self.styles["EncabezadoSeccion"]))

        for i in range(0, len(radares), 2):
            grupo = radares[i:i + 2]
            tabla_data = []
            for nombre, buf in grupo:
                img = Image(buf, width=8 * cm, height=8 * cm)
                tabla_data.append([img])

            if len(grupo) == 1:
                tabla_data.append([""])

            t = Table(tabla_data, colWidths=[9 * cm, 9 * cm])
            t.setStyle(TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            self.elementos.append(t)
            self.elementos.append(Spacer(1, 8))

    def agregar_bloque_clinico(self, riesgos: list[dict], wbgt: float):
        self.elementos.append(PageBreak())
        self.elementos.append(
            Paragraph("Bloque Clínico de Seguridad", self.styles["EncabezadoSeccion"])
        )

        data = [["Jugador", "Posición", "Km", "Riesgo", "Acción Recomendada"]]
        for r in riesgos:
            color = COLOR_MAP.get(r["nivel"], COLOR_BAJO)
            nivel_texto = f'<font color="{color.hexval()}"><b>{r["nivel"]}</b></font>'
            data.append([
                r["jugador"],
                r["posicion"],
                f'{r["km"]:.2f}',
                Paragraph(nivel_texto, self.styles["CeldaTabla"]),
                Paragraph(r["accion"], ParagraphStyle(
                    "accion", parent=self.styles["CeldaTabla"],
                    fontSize=7, alignment=TA_LEFT,
                    textColor=colors.HexColor("#333"),
                )),
            ])

        col_widths = [70, 50, 35, 55, 120]
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ]))
        self.elementos.append(t)
        self.elementos.append(Spacer(1, 10))

        recomendaciones = """
        <b>Recomendaciones generales:</b><br/>
        • Mantener hidratación constante antes, durante y después del partido.<br/>
        • Programar pausas de recuperación en zonas de sombra cada 15-20 minutos.<br/>
        • En niveles ALTO o CRÍTICO, priorizar la salud del atleta sobre la competición.<br/>
        • Monitorear signos de golpe de calor: mareos, náuseas, piel seca, pulso acelerado.<br/>
        • Reportar cualquier síntoma al cuerpo técnico y a los padres de familia de inmediato.
        """
        self.elementos.append(Paragraph(recomendaciones, self.styles["TextoClinico"]))
        self.elementos.append(Spacer(1, 10))

        info_wbgt = (
            f"<b>Índice WBGT del partido:</b> {wbgt}°C &nbsp;|&nbsp; "
            f"<b>Clasificación:</b> {self._clasificar_wbgt(wbgt)}"
        )
        self.elementos.append(Paragraph(info_wbgt, self.styles["TextoClinico"]))

    def _clasificar_wbgt(self, wbgt: float) -> str:
        if wbgt >= 31.1:
            return "CRÍTICO - Suspender actividad prolongada"
        if wbgt >= 29.4:
            return "ALTO - Monitoreo estricto"
        if wbgt >= 27.7:
            return "MODERADO - Precaución"
        return "BAJO - Zona segura"

    def _agregar_pie_pagina(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#999999"))
        canvas.drawCentredString(
            A4[0] / 2, 1 * cm,
            f"SkillRadar v1.0.0 | Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        )
        canvas.restoreState()

    def generar(self) -> io.BytesIO:
        self.doc.build(self.elementos, onFirstPage=self._agregar_pie_pagina,
                       onLaterPages=self._agregar_pie_pagina)
        self.buf.seek(0)
        return self.buf
