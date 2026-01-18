#!/usr/bin/env python3
"""
Butterworth Pi LC Low Pass Filter Calculator

Calculates component values for a Butterworth Pi-topology low-pass filter.
Based on formulas from calculatoredge.com

Pi topology: C1 - L1 - C2 - L2 - C3 ... (shunt caps, series inductors)

Written by Matt N3AR (with AI coding assistance)
"""

import argparse
import math
import sys


def calculate_butterworth_pi_lowpass(cutoff_freq_hz: float, impedance_ohms: float, num_components: int) -> dict:
    """
    Calculate Butterworth Pi low-pass filter component values.

    Args:
        cutoff_freq_hz: Cutoff frequency in Hz
        impedance_ohms: Characteristic impedance in ohms
        num_components: Number of filter components (1-11)

    Returns:
        Dict with 'capacitors' and 'inductors' lists (values in Farads and Henries)
    """
    # Clamp number of components
    n = max(1, min(11, num_components))

    omega = 2 * math.pi * cutoff_freq_hz

    capacitors = []
    inductors = []

    for i in range(1, n + 1):
        # Butterworth g-coefficient
        k = (2 * i - 1) * math.pi / (2 * n)
        g = 2 * math.sin(k)

        # Capacitance and inductance from g-value
        cap_value = g / (impedance_ohms * omega)  # Farads
        ind_value = g * impedance_ohms / omega     # Henries

        # Pi topology: odd positions = capacitors, even positions = inductors
        if i % 2 == 1:
            capacitors.append(cap_value)
        else:
            inductors.append(ind_value)

    return {'capacitors': capacitors, 'inductors': inductors}


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
        description='Butterworth Pi LC Low Pass Filter Calculator',
        epilog='Example: %(prog)s -f 10MHz -z 50 -n 5'
    )
    parser.add_argument('-f', '--frequency', required=True,
                        help='Cutoff frequency (e.g., 100MHz, 1.5GHz, 500kHz)')
    parser.add_argument('-z', '--impedance', default='50',
                        help='Characteristic impedance (default: 50 ohms)')
    parser.add_argument('-n', '--components', type=int, default=3,
                        help='Number of components 1-11 (default: 3)')
    parser.add_argument('--raw', action='store_true',
                        help='Output raw values in Farads and Henries')
    parser.add_argument('--explain', action='store_true',
                        help='Explain how this filter works')

    args = parser.parse_args()

    if args.explain:
        print("""
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

    result = calculate_butterworth_pi_lowpass(freq_hz, impedance, args.components)

    # Display results
    print("\nButterworth Pi Low Pass Filter")
    print(f"{'=' * 40}")
    print(f"Cutoff Frequency: {freq_hz/1e6:.4g} MHz")
    print(f"Impedance Z₀:     {impedance:.4g} Ω")
    print(f"Order:            {len(result['capacitors']) + len(result['inductors'])}")
    print(f"{'=' * 40}")
    print("\nTopology:")
    print("        ┌──────┤ L1 ├──────┬──────┤ L2 ├──────┐")
    print("  IN ───┤                  │                  ├─── OUT")
    print("       ===C1              ===C2              ===C3")
    print("        │                  │                  │")
    print("       GND                GND                GND")
    print(f"\n{'Component Values':^40}")
    print(f"{'-' * 40}")

    # Interleave capacitors and inductors for display
    cap_idx = 0
    ind_idx = 0
    comp_num = 1

    while cap_idx < len(result['capacitors']) or ind_idx < len(result['inductors']):
        if comp_num % 2 == 1 and cap_idx < len(result['capacitors']):
            val = result['capacitors'][cap_idx]
            if args.raw:
                print(f"  C{cap_idx + 1}: {val:.6e} F")
            else:
                print(f"  C{cap_idx + 1}: {format_capacitance(val)}")
            cap_idx += 1
        elif ind_idx < len(result['inductors']):
            val = result['inductors'][ind_idx]
            if args.raw:
                print(f"  L{ind_idx + 1}: {val:.6e} H")
            else:
                print(f"  L{ind_idx + 1}: {format_inductance(val)}")
            ind_idx += 1
        comp_num += 1

    print()


if __name__ == '__main__':
    main()
