import numpy as np
import pandas as pd

COLUMNAS_REQUERIDAS = [
    "Nombre_Jugador", "Posicion", "Minutos",
    "Pases_OK", "Pases_Fallados", "Tiros_Arco",
    "Recuperaciones", "Km_Corridos",
]

POSICIONES = {"Portero", "Defensa", "Medio", "Delantero"}


def validar_columnas(df: pd.DataFrame) -> list[str]:
    faltan = [c for c in COLUMNAS_REQUERIDAS if c not in df.columns]
    return faltan


def validar_datos(df: pd.DataFrame) -> list[str]:
    errores = []
    for idx, row in df.iterrows():
        if row["Posicion"] not in POSICIONES:
            errores.append(f"Fila {idx+2}: Posicion '{row['Posicion']}' inválida")
        if not (1 <= row["Minutos"] <= 90):
            errores.append(f"Fila {idx+2}: Minutos fuera de rango (1-90)")
        if row["Km_Corridos"] < 0:
            errores.append(f"Fila {idx+2}: Km_Corridos negativo")
    return errores


def efectividad_pases(row: pd.Series) -> float:
    total = row["Pases_OK"] + row["Pases_Fallados"]
    if total == 0:
        return 0.0
    return (row["Pases_OK"] / total) * 99.0


def factor_ataque(row: pd.Series) -> float:
    if row["Minutos"] == 0:
        return 0.0
    tiros_por_minuto = row["Tiros_Arco"] / row["Minutos"]
    factor = np.log1p(tiros_por_minuto * 90) * 25
    return min(factor, 99.0)


PESO_DEFENSA_POR_POSICION = {
    "Portero": 1.8,
    "Defensa": 1.4,
    "Medio": 1.0,
    "Delantero": 0.7,
}


def factor_defensa(row: pd.Series) -> float:
    peso = PESO_DEFENSA_POR_POSICION.get(row["Posicion"], 1.0)
    raw = row["Recuperaciones"] * peso
    return min(raw, 99.0)


def escalar_km(row: pd.Series) -> float:
    km = row["Km_Corridos"]
    return min((km / 12.0) * 99.0, 99.0)


def calcular_skill_radar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Distribucion"] = df.apply(efectividad_pases, axis=1)
    df["Ataque"] = df.apply(factor_ataque, axis=1)
    df["Defensa"] = df.apply(factor_defensa, axis=1)
    df["Km_Puntaje"] = df.apply(escalar_km, axis=1)

    def rendimiento_total(row):
        return (row["Distribucion"] + row["Ataque"] + row["Defensa"] + row["Km_Puntaje"]) / 4.0

    df["Rendimiento"] = df.apply(rendimiento_total, axis=1)
    df = df.sort_values("Rendimiento", ascending=False).reset_index(drop=True)
    return df


CATEGORIAS_RADAR = ["Distribucion", "Ataque", "Defensa", "Km_Puntaje"]
ETIQUETAS_RADAR = ["Distribución", "Ataque", "Defensa", "Km Recorridos"]
