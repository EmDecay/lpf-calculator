"""
Transfer function calculations for filter frequency response.

Provides magnitude response |H(jw)| for Butterworth, Chebyshev, and Bessel
low-pass filters across a range of frequencies.
"""

import math


# Bessel polynomial coefficients for orders 2-9
# Source: A.I. Zverev, "Handbook of Filter Synthesis" (1967), Table 4-54
# These are the denominator polynomial coefficients for Bessel filters
# normalized to unit delay at DC. Format: [a0, a1, a2, ..., an] for s^0 to s^n
# Coefficients follow the pattern: a_k = (2n-k)! / (2^(n-k) * k! * (n-k)!)
BESSEL_COEFFS = {
    2: [3, 3, 1],
    3: [15, 15, 6, 1],
    4: [105, 105, 45, 10, 1],
    5: [945, 945, 420, 105, 15, 1],
    6: [10395, 10395, 4725, 1260, 210, 21, 1],
    7: [135135, 135135, 62370, 17325, 3150, 378, 28, 1],
    8: [2027025, 2027025, 945945, 270270, 51975, 6930, 630, 36, 1],
    9: [34459425, 34459425, 16216200, 4729725, 945945, 135135, 13860, 990, 45, 1],
}


def butterworth_response(freq_hz: float, cutoff_hz: float, order: int) -> float:
    """
    Calculate Butterworth filter magnitude response.

    Args:
        freq_hz: Frequency to evaluate
        cutoff_hz: -3dB cutoff frequency
        order: Filter order (number of poles)

    Returns:
        Magnitude |H(jw)| from 0 to 1
    """
    if cutoff_hz <= 0:
        raise ValueError("Cutoff frequency must be positive")
    if order < 1:
        raise ValueError("Order must be at least 1")

    ratio = freq_hz / cutoff_hz
    # |H|² = 1 / (1 + (f/fc)^(2n))
    h_squared = 1.0 / (1.0 + ratio ** (2 * order))
    return math.sqrt(h_squared)


def chebyshev_polynomial(n: int, x: float) -> float:
    """
    Calculate Chebyshev polynomial of the first kind Tn(x).

    Uses recurrence relation: Tn(x) = 2x*Tn-1(x) - Tn-2(x)

    Args:
        n: Polynomial order
        x: Value to evaluate

    Returns:
        Tn(x)
    """
    if n == 0:
        return 1.0
    if n == 1:
        return x

    t_prev2 = 1.0  # T0
    t_prev1 = x    # T1

    for _ in range(2, n + 1):
        t_curr = 2 * x * t_prev1 - t_prev2
        t_prev2 = t_prev1
        t_prev1 = t_curr

    return t_prev1


def chebyshev_response(freq_hz: float, cutoff_hz: float, order: int,
                       ripple_db: float) -> float:
    """
    Calculate Chebyshev Type I filter magnitude response.

    Args:
        freq_hz: Frequency to evaluate
        cutoff_hz: Passband edge frequency (ripple point)
        order: Filter order
        ripple_db: Passband ripple in dB

    Returns:
        Magnitude |H(jw)| from 0 to 1
    """
    if cutoff_hz <= 0:
        raise ValueError("Cutoff frequency must be positive")
    if order < 1:
        raise ValueError("Order must be at least 1")
    if ripple_db <= 0:
        raise ValueError("Ripple must be positive")

    # epsilon from ripple: ε = sqrt(10^(ripple_db/10) - 1)
    epsilon = math.sqrt(10 ** (ripple_db / 10) - 1)

    ratio = freq_hz / cutoff_hz

    # Tn(x) for x = f/fc
    tn = chebyshev_polynomial(order, ratio)

    # |H|² = 1 / (1 + ε²*Tn²(f/fc))
    h_squared = 1.0 / (1.0 + epsilon ** 2 * tn ** 2)
    return math.sqrt(h_squared)


def bessel_response(freq_hz: float, cutoff_hz: float, order: int) -> float:
    """
    Calculate Bessel filter magnitude response.

    Uses polynomial evaluation of Bessel transfer function.
    Bessel filters have maximally flat group delay.

    Args:
        freq_hz: Frequency to evaluate
        cutoff_hz: -3dB cutoff frequency
        order: Filter order (2-9)

    Returns:
        Magnitude |H(jw)| from 0 to 1
    """
    if cutoff_hz <= 0:
        raise ValueError("Cutoff frequency must be positive")
    if order < 2 or order > 9:
        raise ValueError("Order must be between 2 and 9")

    # Bessel filters are normalized to unit group delay, not -3dB cutoff.
    # These scale factors convert to -3dB normalization for consistency.
    # Source: Williams & Taylor, "Electronic Filter Design Handbook" (4th ed.)
    # Values are the frequency at which |H(jw)| = 1/sqrt(2) for each order.
    bessel_scale = {
        2: 1.3617, 3: 1.7557, 4: 2.1139, 5: 2.4274,
        6: 2.7034, 7: 2.9517, 8: 3.1796, 9: 3.3917
    }

    w = (freq_hz / cutoff_hz) * bessel_scale[order]
    coeffs = BESSEL_COEFFS[order]

    # Evaluate |H(jw)|² = |B_n(0)|² / |B_n(jw)|²
    # For Bessel: B_n(s) = sum(coeffs[k] * s^k)
    # At s=jw: alternate real/imag parts

    # Real part: coeffs[0] - coeffs[2]*w² + coeffs[4]*w⁴ - ...
    # Imag part: coeffs[1]*w - coeffs[3]*w³ + coeffs[5]*w⁵ - ...
    real_part = 0.0
    imag_part = 0.0
    w_power = 1.0

    for k, c in enumerate(coeffs):
        if k % 2 == 0:
            # Even power: contributes to real (alternating sign)
            sign = (-1) ** (k // 2)
            real_part += sign * c * w_power
        else:
            # Odd power: contributes to imag (alternating sign)
            sign = (-1) ** (k // 2)
            imag_part += sign * c * w_power
        w_power *= w

    # |H(jw)|² = coeffs[0]² / (real² + imag²)
    dc_gain_squared = coeffs[0] ** 2
    denom_squared = real_part ** 2 + imag_part ** 2

    if denom_squared == 0:
        return 1.0

    h_squared = dc_gain_squared / denom_squared
    return math.sqrt(min(h_squared, 1.0))  # Clamp to 1.0 max


def magnitude_to_db(magnitude: float) -> float:
    """
    Convert magnitude to decibels.

    Args:
        magnitude: Linear magnitude (0 to 1)

    Returns:
        Magnitude in dB, floored at -120 dB for numerical stability
    """
    if magnitude <= 0:
        return -120.0
    db = 20 * math.log10(magnitude)
    return max(db, -120.0)


def frequency_response(filter_type: str, freqs: list[float], cutoff_hz: float,
                       order: int, ripple_db: float = 0.5) -> list[float]:
    """
    Calculate frequency response in dB for a list of frequencies.

    Args:
        filter_type: 'butterworth', 'chebyshev', or 'bessel'
        freqs: List of frequencies in Hz
        cutoff_hz: Cutoff frequency in Hz
        order: Filter order
        ripple_db: Passband ripple for Chebyshev (default 0.5)

    Returns:
        List of magnitude responses in dB
    """
    filter_type = filter_type.lower()

    if filter_type in ('butterworth', 'bw'):
        response_fn = lambda f: butterworth_response(f, cutoff_hz, order)
    elif filter_type in ('chebyshev', 'ch'):
        response_fn = lambda f: chebyshev_response(f, cutoff_hz, order, ripple_db)
    elif filter_type in ('bessel', 'bs'):
        response_fn = lambda f: bessel_response(f, cutoff_hz, order)
    else:
        raise ValueError(f"Unknown filter type: {filter_type}")

    return [magnitude_to_db(response_fn(f)) for f in freqs]
