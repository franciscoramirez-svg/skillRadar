import io

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

from .processing import CATEGORIAS_RADAR, ETIQUETAS_RADAR


def _dibujar_radar(
    valores: list[float],
    titulo: str,
    color: str = "#2196F3",
    tamano: tuple = (4, 4),
) -> io.BytesIO:
    N = len(CATEGORIAS_RADAR)
    angulos = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angulos += angulos[:1]

    vals = valores + valores[:1]

    fig, ax = plt.subplots(figsize=tamano, subplot_kw={"projection": "polar"})
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#1a1a2e")

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    ax.set_rscale("linear")
    ax.set_rlim(0, 99)

    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(ETIQUETAS_RADAR, fontsize=8, fontweight="bold", color="white")

    ax.set_yticks([20, 40, 60, 80])
    ax.set_yticklabels(["20", "40", "60", "80"], fontsize=6, color="gray")
    ax.yaxis.grid(True, color="gray", alpha=0.3)
    ax.xaxis.grid(True, color="gray", alpha=0.3)
    ax.set_ylim(0, 99)

    ax.plot(angulos, vals, "o-", linewidth=2, color=color, alpha=0.9)
    ax.fill(angulos, vals, alpha=0.25, color=color)

    for i, (ang, val) in enumerate(zip(angulos[:-1], valores)):
        ax.annotate(
            f"{val:.0f}",
            xy=(ang, val),
            fontsize=7,
            fontweight="bold",
            color="white",
            ha="center",
            va="bottom",
            textcoords="offset points",
            xytext=(0, 5),
        )

    ax.set_title(titulo, fontsize=11, fontweight="bold", color="white", pad=20)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor="#1a1a2e", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return buf


def generar_radar_jugador(valores: list[float], nombre: str) -> io.BytesIO:
    return _dibujar_radar(valores, nombre)


def generar_radar_plantilla(df_procesado, tamano: tuple = (3.5, 3.5)) -> list[tuple[str, io.BytesIO]]:
    resultados = []
    for _, row in df_procesado.iterrows():
        vals = [row[c] for c in CATEGORIAS_RADAR]
        buf = _dibujar_radar(vals, row["Nombre_Jugador"], tamano=tamano)
        resultados.append((row["Nombre_Jugador"], buf))
    return resultados
