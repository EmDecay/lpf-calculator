"""
Filter calculations for Pi LC low-pass filters.

Contains Butterworth, Chebyshev, and Bessel filter coefficient calculations.
"""

import math


# Bessel normalized g-values for orders 2-9 (standard filter design tables)
# Source: Zverev's Handbook of Filter Synthesis, Matthaei/Young/Jones tables
BESSEL_G_VALUES = {
    2: [0.5755, 2.1478],
    3: [0.3374, 0.9705, 2.2034],
    4: [0.2334, 0.6725, 1.0815, 2.2404],
    5: [0.1743, 0.5072, 0.8040, 1.1110, 2.2582],
    6: [0.1365, 0.4002, 0.6392, 0.8538, 1.1126, 2.2645],
    7: [0.1106, 0.3259, 0.5249, 0.7020, 0.8690, 1.1052, 2.2659],
    8: [0.0919, 0.2719, 0.4409, 0.5936, 0.7303, 0.8695, 1.0956, 2.2656],
    9: [0.0780, 0.2313, 0.3770, 0.5108, 0.6306, 0.7407, 0.8639, 1.0863, 2.2649],
}


def calculate_butterworth(cutoff_hz: float, impedance: float, num_components: int) -> tuple[list[float], list[float], int]:
    """
    Calculate Butterworth Pi low-pass filter component values.

    Args:
        cutoff_hz: Cutoff frequency in Hz
        impedance: Characteristic impedance in Ohms
        num_components: Number of filter elements (2-9)

    Returns:
        Tuple of (capacitors, inductors, order) where capacitors and inductors
        are lists of values in Farads and Henries respectively.
    """
    n = num_components
    omega = 2 * math.pi * cutoff_hz

    capacitors = []
    inductors = []

    for i in range(1, n + 1):
        k = (2 * i - 1) * math.pi / (2 * n)
        g = 2 * math.sin(k)

        cap_value = g / (impedance * omega)
        ind_value = g * impedance / omega

        if i % 2 == 1:
            capacitors.append(cap_value)
        else:
            inductors.append(ind_value)

    return capacitors, inductors, n


def calculate_chebyshev(cutoff_hz: float, impedance: float, ripple_db: float, num_components: int) -> tuple[list[float], list[float], int]:
    """
    Calculate Chebyshev Pi low-pass filter component values.

    Args:
        cutoff_hz: Cutoff frequency in Hz
        impedance: Characteristic impedance in Ohms
        ripple_db: Passband ripple in dB
        num_components: Number of filter elements (2-9)

    Returns:
        Tuple of (capacitors, inductors, order) where capacitors and inductors
        are lists of values in Farads and Henries respectively.
    """
    n = num_components
    omega = 2 * math.pi * cutoff_hz

    rr = ripple_db / 17.37
    e2x = math.exp(2 * rr)
    coth = (e2x + 1) / (e2x - 1)
    bt = math.log(coth)
    btn = bt / (2 * n)
    gn = math.sinh(btn)

    a = [0.0] * (n + 1)
    b = [0.0] * (n + 1)
    g = [0.0] * (n + 1)

    for i in range(1, n + 1):
        k = (2 * i - 1) * math.pi / (2 * n)
        a[i] = math.sin(k)
        k2 = math.pi * i / n
        b[i] = gn ** 2 + math.sin(k2) ** 2

    g[1] = 2 * a[1] / gn
    for i in range(2, n + 1):
        g[i] = (4 * a[i - 1] * a[i]) / (b[i - 1] * g[i - 1])

    capacitors = []
    inductors = []

    for i in range(1, n + 1):
        if i % 2 == 1:
            capacitors.append(g[i] / (impedance * omega))
        else:
            inductors.append(g[i] * impedance / omega)

    return capacitors, inductors, n


def calculate_bessel(cutoff_hz: float, impedance: float, num_components: int) -> tuple[list[float], list[float], int]:
    """
    Calculate Bessel (Thomson) Pi low-pass filter component values.

    Bessel filters provide maximally-flat group delay (linear phase response),
    ideal for pulse/transient applications where waveform preservation matters.

    Args:
        cutoff_hz: Cutoff frequency in Hz
        impedance: Characteristic impedance in Ohms
        num_components: Number of filter elements (2-9)

    Returns:
        Tuple of (capacitors, inductors, order) where capacitors and inductors
        are lists of values in Farads and Henries respectively.
    """
    n = num_components
    omega = 2 * math.pi * cutoff_hz

    g_values = BESSEL_G_VALUES[n]

    capacitors = []
    inductors = []

    for i in range(n):
        g = g_values[i]
        if i % 2 == 0:
            capacitors.append(g / (impedance * omega))
        else:
            inductors.append(g * impedance / omega)

    return capacitors, inductors, n
