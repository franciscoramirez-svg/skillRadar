from enum import Enum

import pandas as pd


class NivelRiesgo(Enum):
    BAJO = "BAJO"
    MODERADO = "MODERADO"
    ALTO = "ALTO"
    CRITICO = "CRÍTICO"


class EstadoCliente:
    def __init__(self, nivel: NivelRiesgo, accion: str, descripcion: str):
        self.nivel = nivel
        self.accion = accion
        self.descripcion = descripcion


WGBT_CRITICO = 31.1
WGBT_ALTO = 29.4
WGBT_MODERADO = 27.7
KM_SUSTITUCION = 5.0
KM_FATIGA = 6.5


def evaluar_riesgo_partido(wbgt: float, km_corridos: float, minutos: int) -> EstadoCliente:
    if wbgt >= WGBT_CRITICO:
        return EstadoCliente(
            nivel=NivelRiesgo.CRITICO,
            accion="SUSPENSIÓN OBLIGATORIA",
            descripcion=(
                "Índice WBGT crítico. Suspender entrenamientos o partidos prolongados. "
                "Riesgo severo de golpe de calor."
            ),
        )

    if wbgt >= WGBT_ALTO:
        if km_corridos > KM_SUSTITUCION:
            return EstadoCliente(
                nivel=NivelRiesgo.ALTO,
                accion="SUSTITUCIÓN RECOMENDADA (OBLIGATORIA)",
                descripcion=(
                    f"WBGT alto ({wbgt}°C) y kilometraje elevado ({km_corridos} km). "
                    "Se recomienda sustitución inmediata del jugador."
                ),
            )
        return EstadoCliente(
            nivel=NivelRiesgo.ALTO,
            accion="MONITOREO ESTRICTO",
            descripcion=(
                f"WBGT alto ({wbgt}°C). Monitorear signos de fatiga y proveer "
                "hidratación constante."
            ),
        )

    if wbgt >= WGBT_MODERADO:
        if km_corridos > KM_FATIGA:
            return EstadoCliente(
                nivel=NivelRiesgo.MODERADO,
                accion="ALERTA DE FATIGA ACUMULADA",
                descripcion=(
                    f"WBGT moderado ({wbgt}°C) con recorrido elevado ({km_corridos} km). "
                    "Activar alertas preventivas de fatiga acumulada. "
                    "Considerar rotación."
                ),
            )
        return EstadoCliente(
            nivel=NivelRiesgo.MODERADO,
            accion="PRECAUCIÓN",
            descripcion=(
                f"WBGT moderado ({wbgt}°C). Mantener hidratación y pausas activas."
            ),
        )

    return EstadoCliente(
        nivel=NivelRiesgo.BAJO,
        accion="RENDIMIENTO ÓPTIMO",
        descripcion=(
            "Zona de rendimiento óptimo seguro. Continuar con la estrategia planificada."
        ),
    )


def evaluar_todos(df_procesado: pd.DataFrame, wbgt: float) -> list[dict]:
    resultados = []
    for _, row in df_procesado.iterrows():
        estado = evaluar_riesgo_partido(wbgt, row["Km_Corridos"], row["Minutos"])
        resultados.append({
            "jugador": row["Nombre_Jugador"],
            "posicion": row["Posicion"],
            "km": row["Km_Corridos"],
            "nivel": estado.nivel.value,
            "accion": estado.accion,
            "descripcion": estado.descripcion,
        })
    return resultados
