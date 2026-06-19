import numpy as np


def presion_vapor(temp_c: float, humedad_relativa: float) -> float:
    """
    Calcula la presión de vapor de agua (e) en hPa
    usando la fórmula de Magnus.
    """
    if temp_c < 0:
        return 0.0
    es = 6.112 * np.exp((17.67 * temp_c) / (temp_c + 243.5))
    e = es * (humedad_relativa / 100.0)
    return e


def calcular_wbgt(temp_c: float, humedad_relativa: float) -> float:
    """
    Fórmula simplificada OMM:
    WBGT = (0.567 × T) + (0.393 × e) + 3.94
    """
    e = presion_vapor(temp_c, humedad_relativa)
    wbgt = (0.567 * temp_c) + (0.393 * e) + 3.94
    return round(wbgt, 2)
