#!/usr/bin/env python3
"""
Pi LC Low Pass Filter Calculator

Calculates component values for Butterworth or Chebyshev Pi-topology low-pass filters.
Based on formulas from calculatoredge.com

Pi topology: C1 - L1 - C2 - L2 - C3 ... (shunt caps, series inductors)

Written by Matt N3AR (with AI coding assistance)
"""

import argparse
import sys

from lowpass_lib import (
    calculate_butterworth,
    calculate_chebyshev,
    display_results,
    parse_frequency,
    parse_impedance,
)


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
        result = {
            'filter_type': 'butterworth',
            'freq_hz': freq_hz,
            'impedance': impedance,
            'capacitors': capacitors,
            'inductors': inductors,
            'order': order,
            'ripple': None,
        }
    else:
        if args.ripple <= 0:
            print("Error: Ripple must be positive", file=sys.stderr)
            sys.exit(1)
        capacitors, inductors, order = calculate_chebyshev(freq_hz, impedance, args.ripple, args.components)
        result = {
            'filter_type': 'chebyshev',
            'freq_hz': freq_hz,
            'impedance': impedance,
            'capacitors': capacitors,
            'inductors': inductors,
            'order': order,
            'ripple': args.ripple,
        }

    display_results(result, raw=args.raw)


if __name__ == '__main__':
    main()
