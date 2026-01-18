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


def format_value(value: float, unit_type: str) -> str:
    """Format component value with appropriate SI prefix."""
    if unit_type == "capacitance":
        if value >= 1e-6:
            return f"{value * 1e6:.4f} µF"
        elif value >= 1e-9:
            return f"{value * 1e9:.4f} nF"
        else:
            return f"{value * 1e12:.4f} pF"
    else:  # inductance
        if value >= 1:
            return f"{value:.4f} H"
        elif value >= 1e-3:
            return f"{value * 1e3:.4f} mH"
        elif value >= 1e-6:
            return f"{value * 1e6:.4f} µH"
        else:
            return f"{value * 1e9:.4f} nH"


def parse_frequency(freq_str: str) -> float:
    """Parse frequency string with optional unit suffix."""
    freq_str = freq_str.strip().upper()
    # Order matters: check longer suffixes first
    multipliers = [
        ('MHZ', 1e6), ('GHZ', 1e9), ('KHZ', 1e3), ('HZ', 1),
        ('M', 1e6), ('G', 1e9), ('K', 1e3), ('H', 1),
    ]
    for suffix, mult in multipliers:
        if freq_str.endswith(suffix):
            return float(freq_str[:-len(suffix)]) * mult
    return float(freq_str)


def parse_impedance(z_str: str) -> float:
    """Parse impedance string with optional unit suffix."""
    z_str = z_str.strip().upper()
    # Order matters: check longer suffixes first
    multipliers = [
        ('KOHMS', 1e3), ('KOHM', 1e3), ('MOHMS', 1e6), ('MOHM', 1e6),
        ('OHMS', 1), ('OHM', 1), ('K', 1e3),
    ]
    for suffix, mult in multipliers:
        if z_str.endswith(suffix):
            return float(z_str[:-len(suffix)]) * mult
    return float(z_str)


def main():
    parser = argparse.ArgumentParser(
        description="Chebyshev Pi LC Low Pass Filter Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -f 100MHz -z 50 -r 0.5 -n 5
  %(prog)s --freq 14.2M --impedance 50 --ripple 0.1 --order 7
  %(prog)s -f 1GHz -z 75ohm -r 0.25 -n 3

Notes:
  - Filter order (n) must be odd for Pi topology; even values are incremented
  - Frequency accepts suffixes: Hz, KHz, MHz, GHz (or H, K, M, G)
  - Impedance accepts suffixes: ohm, Kohm, Mohm
        """
    )
    parser.add_argument(
        '-f', '--freq', required=True,
        help='Cutoff frequency (e.g., 100MHz, 1.5GHz, 14200000)'
    )
    parser.add_argument(
        '-z', '--impedance', required=True,
        help='Characteristic impedance in ohms (e.g., 50, 75ohm)'
    )
    parser.add_argument(
        '-r', '--ripple', type=float, required=True,
        help='Passband ripple in dB (e.g., 0.5, 0.1)'
    )
    parser.add_argument(
        '-n', '--order', type=int, required=True,
        help='Number of components/filter order (1-11)'
    )
    parser.add_argument(
        '--explain', action='store_true',
        help='Explain how this filter works'
    )

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
        freq = parse_frequency(args.freq)
        impedance = parse_impedance(args.impedance)
    except ValueError as e:
        print(f"Error parsing input: {e}", file=sys.stderr)
        sys.exit(1)

    if args.ripple <= 0:
        print("Error: Ripple must be positive", file=sys.stderr)
        sys.exit(1)

    capacitors, inductors, actual_n = calculate_chebyshev_pi_lowpass(
        freq, impedance, args.ripple, args.order
    )

    # Display results
    print("\n" + "=" * 50)
    print("  Chebyshev Pi LC Low Pass Filter")
    print("=" * 50)
    print(f"  Cutoff Frequency: {freq/1e6:.6g} MHz")
    print(f"  Impedance:        {impedance:.6g} Ω")
    print(f"  Ripple:           {args.ripple} dB")
    print(f"  Order:            {actual_n}")
    if actual_n != args.order:
        print(f"  (adjusted from {args.order} to {actual_n} for Pi topology)")
    print("=" * 50)

    print("\n  Topology:")
    print("          ┌──────┤ L1 ├──────┬──────┤ L2 ├──────┐")
    print("    IN ───┤                  │                  ├─── OUT")
    print("         ===C1              ===C2              ===C3")
    print("          │                  │                  │")
    print("         GND                GND                GND")

    print("\n  Component Values:")
    print("  " + "-" * 46)

    # Pi filter: C-L-C-L-C... pattern
    # Display in circuit order
    c_idx = 0
    l_idx = 0

    for i in range(1, actual_n + 1):
        if i % 2 == 1:  # Capacitor (shunt)
            val = format_value(capacitors[c_idx], "capacitance")
            print(f"  C{c_idx + 1}: {val:>20}")
            c_idx += 1
        else:  # Inductor (series)
            val = format_value(inductors[l_idx], "inductance")
            print(f"  L{l_idx + 1}: {val:>20}")
            l_idx += 1

    print("  " + "-" * 46)
    print()


if __name__ == "__main__":
    main()
