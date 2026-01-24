"""
E-series component matching for filter design.

Provides standard E-series values (E12, E24, E96) and algorithms to find
the closest matching standard component values, including parallel combinations.
"""

import math
from dataclasses import dataclass


# E-series normalized values (1.0 to <10.0)
# These are logarithmically spaced standard resistor/capacitor/inductor values

E12_VALUES = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]

E24_VALUES = [
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
]

E96_VALUES = [
    1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30,
    1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
    1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32,
    2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
    3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
    4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49,
    5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32,
    7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76
]

SERIES_MAP = {
    'E12': E12_VALUES,
    'E24': E24_VALUES,
    'E96': E96_VALUES,
}


@dataclass
class MatchResult:
    """Result of E-series component matching."""
    ideal_value: float
    matched_value: float
    error_percent: float
    series: str
    parallel_values: tuple[float, float] | None = None
    parallel_error_percent: float | None = None


def get_eseries_values(series: str) -> list[float]:
    """Get normalized E-series values for given series name."""
    series_upper = series.upper()
    if series_upper not in SERIES_MAP:
        raise ValueError(f"Unknown series: {series}. Use E12, E24, or E96.")
    return SERIES_MAP[series_upper]


def normalize_to_decade(value: float) -> tuple[float, int]:
    """
    Extract mantissa and exponent from a value.

    Args:
        value: Any positive number

    Returns:
        Tuple of (mantissa, exponent) where mantissa is in [1.0, 10.0)
        and value = mantissa * 10^exponent
    """
    if value <= 0:
        raise ValueError("Value must be positive")

    exponent = math.floor(math.log10(value))
    mantissa = value / (10 ** exponent)

    # Handle edge case where mantissa rounds to 10.0
    if mantissa >= 10.0:
        mantissa /= 10
        exponent += 1

    return mantissa, exponent


def find_closest(value: float, series: str) -> tuple[float, float]:
    """
    Find closest E-series value for any input value.

    Args:
        value: Target value (any unit - pF, uH, etc.)
        series: E-series name (E12, E24, E96)

    Returns:
        Tuple of (matched_value, error_percent)
    """
    mantissa, exponent = normalize_to_decade(value)
    eseries = get_eseries_values(series)

    # Find closest in normalized range using early-exit optimization
    # E-series values are sorted, so once diff starts increasing we can stop
    best_match = eseries[0]
    best_diff = abs(mantissa - best_match)

    for e_val in eseries[1:]:
        diff = abs(mantissa - e_val)
        if diff < best_diff:
            best_diff = diff
            best_match = e_val
        elif diff > best_diff and e_val > mantissa:
            # Values are sorted, diff will only increase from here
            break

    # Also check wrapping: value near 1.0 might be closer to 10*prev_decade
    # e.g., 0.95 normalized is actually 9.5 in prev decade, closest to 9.1 E24
    if mantissa < eseries[0]:
        # Check if last value of previous decade is closer
        last_val = eseries[-1] / 10
        if abs(mantissa - last_val) < best_diff:
            best_match = last_val

    # Check if first value of next decade is closer (for values near 9.x)
    first_val_next = eseries[0] * 10
    if mantissa > eseries[-1] and abs(mantissa - first_val_next) < abs(mantissa - best_match):
        best_match = first_val_next
        exponent -= 1  # Adjust exponent since we used next decade

    matched_value = best_match * (10 ** exponent)
    error_percent = 100 * (matched_value - value) / value

    return matched_value, error_percent


def find_parallel_match(value: float, series: str) -> tuple[float, float, float] | None:
    """
    Find parallel combination of two E-series values closer to target.

    For capacitors: C_parallel = C1 + C2
    For inductors: 1/L_parallel = 1/L1 + 1/L2

    This function finds the best additive parallel (like capacitors).
    For inductors, caller should use reciprocal values.

    Args:
        value: Target value
        series: E-series name

    Returns:
        Tuple of (val1, val2, error_percent) or None if no improvement >2%
    """
    single_match, single_error = find_closest(value, series)

    # Only search if single match error > 2%
    if abs(single_error) <= 2.0:
        return None

    eseries = get_eseries_values(series)
    mantissa, exponent = normalize_to_decade(value)
    scale = 10 ** exponent

    best_combo: tuple[float, float, float] | None = None
    best_error = abs(single_error)

    # Search for parallel combinations
    # For additive parallel (capacitors): target = v1 + v2
    # We need values from current decade and one below
    decades_to_check = [0, -1]

    all_scaled_values = []
    for d in decades_to_check:
        for e_val in eseries:
            all_scaled_values.append(e_val * scale * (10 ** d))

    # Limit to values within 10x ratio of each other
    for i, v1 in enumerate(all_scaled_values):
        for v2 in all_scaled_values[i:]:
            if v2 > 0 and v1 > 0:
                ratio = max(v1, v2) / min(v1, v2)
                if ratio > 10:
                    continue

                combined = v1 + v2
                error = abs(100 * (combined - value) / value)

                if error < best_error:
                    best_error = error
                    best_combo = (v1, v2, 100 * (combined - value) / value)

    # Only return if improvement > 2%
    if best_combo and (abs(single_error) - best_error) > 2.0:
        return best_combo

    return None


def match_component(value: float, series: str = 'E24') -> MatchResult:
    """
    Match a component value to E-series with optional parallel combination.

    Args:
        value: Ideal component value
        series: E-series to use (E12, E24, E96)

    Returns:
        MatchResult with matched value and optional parallel suggestion
    """
    matched_value, error_percent = find_closest(value, series)

    parallel = find_parallel_match(value, series)
    parallel_values = None
    parallel_error = None

    if parallel:
        parallel_values = (parallel[0], parallel[1])
        parallel_error = parallel[2]

    return MatchResult(
        ideal_value=value,
        matched_value=matched_value,
        error_percent=error_percent,
        series=series.upper(),
        parallel_values=parallel_values,
        parallel_error_percent=parallel_error,
    )
