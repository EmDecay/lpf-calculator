"""
Filter calculations for Pi LC low-pass filters.

Contains Butterworth and Chebyshev filter coefficient calculations.
"""

import math


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
