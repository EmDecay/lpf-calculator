#!/usr/bin/env python3
"""
Pi LC Low Pass Filter Calculator

Calculates component values for Butterworth or Chebyshev Pi-topology low-pass filters.
Based on formulas from calculatoredge.com

Pi topology: C1 - L1 - C2 - L2 - C3 ... (shunt caps, series inductors)

Written by Matt N3AR (with AI coding assistance)
"""

import argparse
import math
import sys


BUTTERWORTH_EXPLANATION = """
Butterworth Low-Pass Filter Explained
======================================

A low-pass filter allows low-frequency signals to pass through while blocking
high-frequency signals.

The Butterworth filter has the smoothest possible response in the passband. This
means signals below the cutoff frequency pass through with almost no change in
volume - the response is "maximally flat." The tradeoff is that it doesn't cut
off as sharply as other filter types, so some unwanted high frequencies still
sneak through near the cutoff point.

This calculator uses a "Pi" topology, named because the circuit diagram looks
like the Greek letter Pi. It alternates between capacitors (connected to ground)
and inductors (in the signal path). The capacitors act like shortcuts to ground
for high frequencies, while the inductors resist rapid changes in current.
Together, they work as a team to block high-frequency signals while letting low
frequencies pass unchanged.

Higher-order filters (more components) give you a steeper cutoff - they're better
at blocking unwanted frequencies, but require more parts to build.

Choose Butterworth over Chebyshev when you need the flattest possible frequency
response and can tolerate a wider cutoff.
"""

CHEBYSHEV_EXPLANATION = """
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
"""


def calculate_butterworth(cutoff_hz: float, impedance: float, num_components: int) -> tuple[list[float], list[float], int]:
    """Calculate Butterworth Pi low-pass filter component values."""
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
    """Calculate Chebyshev Pi low-pass filter component values."""
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


def format_capacitance(value_farads: float) -> str:
    """Format capacitance with appropriate unit."""
    if value_farads >= 1e-3:
        return f"{value_farads * 1e3:.2f} mF"
    elif value_farads >= 1e-6:
        return f"{value_farads * 1e6:.2f} µF"
    elif value_farads >= 1e-9:
        return f"{value_farads * 1e9:.2f} nF"
    else:
        return f"{value_farads * 1e12:.2f} pF"


def format_inductance(value_henries: float) -> str:
    """Format inductance with appropriate unit."""
    if value_henries >= 1:
        return f"{value_henries:.2f} H"
    elif value_henries >= 1e-3:
        return f"{value_henries * 1e3:.2f} mH"
    elif value_henries >= 1e-6:
        return f"{value_henries * 1e6:.2f} µH"
    else:
        return f"{value_henries * 1e9:.2f} nH"


def parse_frequency(freq_str: str) -> float:
    """Parse frequency string with optional unit suffix (Hz, kHz, MHz, GHz)."""
    freq_str = freq_str.strip()
    freq_str_lower = freq_str.lower()

    suffixes = [('ghz', 1e9), ('mhz', 1e6), ('khz', 1e3), ('hz', 1)]

    for suffix, mult in suffixes:
        if freq_str_lower.endswith(suffix):
            num_part = freq_str[:-len(suffix)].strip()
            return float(num_part) * mult

    return float(freq_str)


def parse_impedance(z_str: str) -> float:
    """Parse impedance string with optional unit suffix (ohm, kohm, mohm)."""
    z_str = z_str.strip().lower().replace('ω', 'ohm').replace('Ω', 'ohm')
    multipliers = {'mohm': 1e6, 'kohm': 1e3, 'ohm': 1}

    for suffix, mult in multipliers.items():
        if z_str.endswith(suffix):
            return float(z_str[:-len(suffix)].strip()) * mult

    return float(z_str)


def display_results(filter_type: str, freq_hz: float, impedance: float,
                    capacitors: list[float], inductors: list[float],
                    order: int, ripple: float = None, raw: bool = False):
    """Display calculated filter component values."""
    title = f"{filter_type.title()} Pi Low Pass Filter"
    print(f"\n{title}")
    print(f"{'=' * 40}")
    print(f"Cutoff Frequency: {freq_hz/1e6:.4g} MHz")
    print(f"Impedance Z₀:     {impedance:.4g} Ω")
    if ripple is not None:
        print(f"Ripple:           {ripple} dB")
    print(f"Order:            {order}")
    print(f"{'=' * 40}")
    print("\nTopology:")
    print("        ┌──────┤ L1 ├──────┬──────┤ L2 ├──────┬─ ··· ─┐")
    print("  IN ───┤                  │                  │       ├─── OUT")
    print("       ===C1              ===C2              ===C3   ===Cn")
    print("        │                  │                  │       │")
    print("       GND                GND                GND     GND")
    print(f"\n{'Component Values':^40}")
    print(f"┌{'─' * 19}┬{'─' * 19}┐")
    print(f"│{'Capacitors':^19}│{'Inductors':^19}│")
    print(f"├{'─' * 19}┼{'─' * 19}┤")

    max_rows = max(len(capacitors), len(inductors))
    for i in range(max_rows):
        if i < len(capacitors):
            val = capacitors[i]
            if raw:
                cap_str = f"C{i + 1}: {val:.6e} F"
            else:
                cap_str = f"C{i + 1}: {format_capacitance(val)}"
        else:
            cap_str = ""

        if i < len(inductors):
            val = inductors[i]
            if raw:
                ind_str = f"L{i + 1}: {val:.6e} H"
            else:
                ind_str = f"L{i + 1}: {format_inductance(val)}"
        else:
            ind_str = ""

        print(f"│ {cap_str:<17} │ {ind_str:<17} │")

    print(f"└{'─' * 19}┴{'─' * 19}┘")
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Pi LC Low Pass Filter Calculator (Butterworth or Chebyshev)',
        epilog='Examples:\n'
               '  %(prog)s -t butterworth -f 10MHz -z 50 -n 5\n'
               '  %(prog)s -t chebyshev -f 100MHz -z 50 -r 0.5 -n 5',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-t', '--type', choices=['butterworth', 'chebyshev'],
                        required=True, help='Filter type: butterworth or chebyshev')
    parser.add_argument('-f', '--frequency',
                        help='Cutoff frequency (e.g., 100MHz, 1.5GHz, 500kHz)')
    parser.add_argument('-z', '--impedance', default='50',
                        help='Characteristic impedance (default: 50 ohms)')
    parser.add_argument('-r', '--ripple', type=float, default=0.5,
                        help='Passband ripple in dB for Chebyshev (default: 0.5)')
    parser.add_argument('-n', '--components', type=int, default=3,
                        help='Number of components/poles: 2-9 (default: 3)')
    parser.add_argument('--raw', action='store_true',
                        help='Output raw values in Farads and Henries')
    parser.add_argument('--explain', action='store_true',
                        help='Explain how the selected filter type works')

    args = parser.parse_args()

    if args.explain:
        if args.type == 'butterworth':
            print(BUTTERWORTH_EXPLANATION)
        else:
            print(CHEBYSHEV_EXPLANATION)
        sys.exit(0)

    if not args.frequency:
        parser.error('the following arguments are required: -f/--frequency')

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
    if args.components < 2 or args.components > 9:
        print("Error: Number of components must be between 2 and 9", file=sys.stderr)
        sys.exit(1)

    if args.type == 'butterworth':
        capacitors, inductors, order = calculate_butterworth(freq_hz, impedance, args.components)
        display_results('butterworth', freq_hz, impedance, capacitors, inductors,
                        order, raw=args.raw)
    else:
        if args.ripple <= 0:
            print("Error: Ripple must be positive", file=sys.stderr)
            sys.exit(1)
        capacitors, inductors, order = calculate_chebyshev(freq_hz, impedance, args.ripple, args.components)
        display_results('chebyshev', freq_hz, impedance, capacitors, inductors,
                        order, ripple=args.ripple, raw=args.raw)


if __name__ == '__main__':
    main()
