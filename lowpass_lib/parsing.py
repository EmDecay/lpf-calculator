"""
Input parsing utilities for filter calculators.

Contains parsers for frequency and impedance strings with unit suffixes.
"""


def parse_frequency(freq_str: str) -> float:
    """
    Parse frequency string with optional unit suffix.

    Supported formats:
        - Plain number: 14200000 (Hz)
        - With Hz suffix: 14.2MHz, 500kHz, 1GHz
        - Case insensitive: 14.2mhz, 14.2MHZ

    Args:
        freq_str: Frequency string to parse

    Returns:
        Frequency in Hz

    Raises:
        ValueError: If string cannot be parsed
    """
    freq_str = freq_str.strip()
    freq_str_lower = freq_str.lower()

    suffixes = [('ghz', 1e9), ('mhz', 1e6), ('khz', 1e3), ('hz', 1)]

    for suffix, mult in suffixes:
        if freq_str_lower.endswith(suffix):
            num_part = freq_str[:-len(suffix)].strip()
            return float(num_part) * mult

    return float(freq_str)


def parse_impedance(z_str: str) -> float:
    """
    Parse impedance string with optional unit suffix.

    Supported formats:
        - Plain number: 50
        - With ohm suffix: 50ohm, 1kohm
        - Unicode omega: 50Ohm

    Args:
        z_str: Impedance string to parse

    Returns:
        Impedance in Ohms

    Raises:
        ValueError: If string cannot be parsed
    """
    z_str = z_str.strip().lower().replace('omega', 'ohm').replace('ohm', 'ohm')
    multipliers = {'mohm': 1e6, 'kohm': 1e3, 'ohm': 1}

    for suffix, mult in multipliers.items():
        if z_str.endswith(suffix):
            return float(z_str[:-len(suffix)].strip()) * mult

    return float(z_str)
