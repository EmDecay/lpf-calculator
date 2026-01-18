#!/usr/bin/env python3
"""
Chebyshev Pi LC Low Pass Filter Calculator

Calculates capacitor and inductor values for a Chebyshev Pi-topology
low-pass filter given cutoff frequency, impedance, ripple, and order.

Written by Matt N3AR (with AI coding assistance)
"""

import argparse
import math
import sys


def calculate_chebyshev_pi_lowpass(
    cutoff_hz: float,
    impedance_ohm: float,
    ripple_db: float,
    num_components: int
) -> tuple[list[float], list[float]]:
    """
    Calculate component values for Chebyshev Pi low-pass filter.

    Args:
        cutoff_hz: Cutoff frequency in Hz
        impedance_ohm: Characteristic impedance in Ohms
        ripple_db: Passband ripple in dB
        num_components: Filter order (1-11, will be adjusted to odd)

    Returns:
        Tuple of (capacitors_farads, inductors_henrys)
    """
    # Clamp and adjust n to be odd (Pi filter requirement)
    n = max(1, min(11, num_components))
    if n % 2 == 0:
        n += 1

    # Angular frequency
    w = 2 * math.pi * cutoff_hz

    # Chebyshev ripple factor calculations
    rr = ripple_db / 17.37
    e2x = math.exp(2 * rr)
    coth = (e2x + 1) / (e2x - 1)
    bt = math.log(coth)
    btn = bt / (2 * n)
    gn = math.sinh(btn)  # (exp(btn) - exp(-btn)) / 2

    # Calculate intermediate arrays
    a = [0.0] * (n + 1)
    b = [0.0] * (n + 1)
    g = [0.0] * (n + 1)

    for i in range(1, n + 1):
        k = (2 * i - 1) * math.pi / (2 * n)
        a[i] = math.sin(k)
        k2 = math.pi * i / n
        b[i] = gn ** 2 + math.sin(k2) ** 2

    # Calculate normalized g values (prototype element values)
    g[1] = 2 * a[1] / gn
    for i in range(2, n + 1):
        g[i] = (4 * a[i - 1] * a[i]) / (b[i - 1] * g[i - 1])

    # Denormalize to actual component values
    # Odd indices -> capacitors (shunt), Even indices -> inductors (series)
    capacitors = []
    inductors = []

    for i in range(1, n + 1):
        if i % 2 == 1:  # Odd: capacitor
            capacitors.append(g[i] / (impedance_ohm * w))
        else:  # Even: inductor
            inductors.append(g[i] * impedance_ohm / w)

    return capacitors, inductors, n


def format_capacitance(value_farads: float) -> str:
    """Format capacitance with appropriate unit."""
    if value_farads >= 1e-3:
        return f"{value_farads * 1e3:.4g} mF"
    elif value_farads >= 1e-6:
        return f"{value_farads * 1e6:.4g} µF"
    elif value_farads >= 1e-9:
        return f"{value_farads * 1e9:.4g} nF"
    else:
        return f"{value_farads * 1e12:.4g} pF"


def format_inductance(value_henries: float) -> str:
    """Format inductance with appropriate unit."""
    if value_henries >= 1:
        return f"{value_henries:.4g} H"
    elif value_henries >= 1e-3:
        return f"{value_henries * 1e3:.4g} mH"
    elif value_henries >= 1e-6:
        return f"{value_henries * 1e6:.4g} µH"
    else:
        return f"{value_henries * 1e9:.4g} nH"


def parse_frequency(freq_str: str) -> float:
    """Parse frequency string with optional unit suffix (Hz, kHz, MHz, GHz)."""
    freq_str = freq_str.strip()
    freq_str_lower = freq_str.lower()

    # Check from longest suffix to shortest to avoid partial matches
    suffixes = [('ghz', 1e9), ('mhz', 1e6), ('khz', 1e3), ('hz', 1)]

    for suffix, mult in suffixes:
        if freq_str_lower.endswith(suffix):
            num_part = freq_str[:-len(suffix)].strip()
            return float(num_part) * mult

    # No suffix, assume Hz
    return float(freq_str)


def parse_impedance(z_str: str) -> float:
    """Parse impedance string with optional unit suffix (ohm, kohm, mohm)."""
    z_str = z_str.strip().lower().replace('ω', 'ohm').replace('Ω', 'ohm')
    multipliers = {'mohm': 1e6, 'kohm': 1e3, 'ohm': 1}

    for suffix, mult in multipliers.items():
        if z_str.endswith(suffix):
            return float(z_str[:-len(suffix)].strip()) * mult

    # No suffix, assume ohms
    return float(z_str)


def main():
    parser = argparse.ArgumentParser(
        description='Chebyshev Pi LC Low Pass Filter Calculator',
        epilog='Example: %(prog)s -f 10MHz -z 50 -r 0.5 -n 5'
    )
    parser.add_argument('-f', '--frequency', required=True,
                        help='Cutoff frequency (e.g., 100MHz, 1.5GHz, 500kHz)')
    parser.add_argument('-z', '--impedance', default='50',
                        help='Characteristic impedance (default: 50 ohms)')
    parser.add_argument('-r', '--ripple', type=float, default=0.5,
                        help='Passband ripple in dB (default: 0.5)')
    parser.add_argument('-n', '--components', type=int, default=3,
                        help='Number of components 1-11 (default: 3)')
    parser.add_argument('--raw', action='store_true',
                        help='Output raw values in Farads and Henries')
    parser.add_argument('--explain', action='store_true',
                        help='Explain how this filter works')

    args = parser.parse_args()

    if args.explain:
        print("""
Chebyshev Low-Pass Filter Explained
====================================

A low-pass filter allows low-frequency signals to pass through while blocking
high-frequency signals.

The Chebyshev filter trades a perfectly smooth passband for a much sharper
cutoff. Unlike the Butterworth filter (which is perfectly flat), the Chebyshev
allows small "ripples" in the passband - tiny variations in signal strength.
In exchange, it cuts off unwanted frequencies much more aggressively.

The "ripple" parameter controls this tradeoff. A smaller ripple (like 0.1 dB)
means the passband is almost flat, but the cutoff is less sharp. A larger ripple
(like 1 dB) gives you a steeper cutoff, but more variation in your passband.
For most applications, 0.5 dB or less is a good starting point.

This calculator uses a "Pi" topology, named because the circuit looks like the
Greek letter Pi. Capacitors connect to ground and act as shortcuts for high
frequencies, while inductors in the signal path resist rapid changes. Together,
they block high frequencies while passing low ones.
              
Higher-order filters (more components) give you a steeper cutoff - they're better
at blocking unwanted frequencies, but require more parts to build.

Choose Chebyshev over Butterworth when you need the sharpest possible cutoff and
can tolerate small ripples in your passband.
""")
        sys.exit(0)

    try:
        freq_hz = parse_frequency(args.frequency)
        impedance = parse_impedance(args.impedance)
    except ValueError as e:
        print(f"Error parsing input: {e}", file=sys.stderr)
        sys.exit(1)

    if freq_hz <= 0:
        print("Error: Frequency must be positive", file=sys.stderr)
        sys.exit(1)
    if impedance <= 0:
        print("Error: Impedance must be positive", file=sys.stderr)
        sys.exit(1)
    if args.ripple <= 0:
        print("Error: Ripple must be positive", file=sys.stderr)
        sys.exit(1)

    capacitors, inductors, actual_n = calculate_chebyshev_pi_lowpass(
        freq_hz, impedance, args.ripple, args.components
    )

    # Display results
    print("\nChebyshev Pi Low Pass Filter")
    print(f"{'=' * 40}")
    print(f"Cutoff Frequency: {freq_hz/1e6:.4g} MHz")
    print(f"Impedance Z₀:     {impedance:.4g} Ω")
    print(f"Ripple:           {args.ripple} dB")
    print(f"Order:            {actual_n}")
    if actual_n != args.components:
        print(f"(adjusted from {args.components} to {actual_n} for Pi topology)")
    print(f"{'=' * 40}")
    print("\nTopology:")
    print("        ┌──────┤ L1 ├──────┬──────┤ L2 ├──────┐")
    print("  IN ───┤                  │                  ├─── OUT")
    print("       ===C1              ===C2              ===C3")
    print("        │                  │                  │")
    print("       GND                GND                GND")
    print(f"\n{'Component Values':^40}")
    print(f"{'-' * 40}")

    # Pi filter: C-L-C-L-C... pattern
    # Display in circuit order
    cap_idx = 0
    ind_idx = 0

    for i in range(1, actual_n + 1):
        if i % 2 == 1:  # Capacitor (shunt)
            val = capacitors[cap_idx]
            if args.raw:
                print(f"  C{cap_idx + 1}: {val:.6e} F")
            else:
                print(f"  C{cap_idx + 1}: {format_capacitance(val)}")
            cap_idx += 1
        else:  # Inductor (series)
            val = inductors[ind_idx]
            if args.raw:
                print(f"  L{ind_idx + 1}: {val:.6e} H")
            else:
                print(f"  L{ind_idx + 1}: {format_inductance(val)}")
            ind_idx += 1

    print()


if __name__ == "__main__":
    main()
