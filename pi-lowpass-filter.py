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
    calculate_bessel,
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

BESSEL_EXPLANATION = """
Bessel (Thomson) Low-Pass Filter Explained
===========================================

A low-pass filter allows low-frequency signals to pass through while blocking
high-frequency signals.

The Bessel filter (also called Thomson filter) is designed for maximally-flat
group delay, which means all frequencies within the passband experience the same
time delay. This results in linear phase response - the filter preserves the
shape of signals passing through it.

This makes Bessel filters ideal for:
- Pulse and transient applications where waveform shape matters
- Digital communications where timing relationships must be preserved
- Audio applications requiring phase coherence
- Any application where overshoot and ringing are unacceptable

The tradeoff is that Bessel filters have the gentlest rolloff of the three types.
They don't attenuate unwanted frequencies as aggressively as Butterworth or
Chebyshev filters. If sharp frequency selectivity is your priority, choose one
of those instead.

This calculator uses a "Pi" topology, named because the circuit looks like the
Greek letter Pi. Capacitors connect to ground and act as shortcuts for high
frequencies, while inductors in the signal path resist rapid changes. Together,
they block high frequencies while passing low ones.

Choose Bessel when signal integrity and waveform preservation are more important
than sharp frequency cutoff.
"""


def resolve_filter_type(alias: str) -> str:
    """Convert short aliases to full filter type names."""
    return {'bw': 'butterworth', 'b': 'butterworth',
            'ch': 'chebyshev', 'c': 'chebyshev',
            'bs': 'bessel'}.get(alias, alias)


def main():
    parser = argparse.ArgumentParser(
        description='Pi LC Low Pass Filter Calculator (Butterworth, Chebyshev, or Bessel)',
        epilog='Examples:\n'
               '  %(prog)s butterworth 10MHz              # positional args\n'
               '  %(prog)s bw 10MHz -n 5                  # short alias\n'
               '  %(prog)s -t chebyshev -f 100MHz -r 0.5  # flags\n'
               '  %(prog)s bessel 10MHz                   # Bessel filter\n'
               '  %(prog)s bw 10MHz --format json         # JSON output\n'
               '  %(prog)s bw 10MHz -q                    # quiet mode',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Positional arguments (optional, fall back to flags)
    parser.add_argument('filter_type', nargs='?',
                        choices=['butterworth', 'chebyshev', 'bessel', 'bw', 'ch', 'bs', 'b', 'c'],
                        help='Filter type (butterworth/bw, chebyshev/ch, or bessel/bs)')
    parser.add_argument('frequency', nargs='?',
                        help='Cutoff frequency (e.g., 10MHz, 1.5GHz)')

    # Keep flags as alternatives
    parser.add_argument('-t', '--type', dest='type_flag',
                        choices=['butterworth', 'chebyshev', 'bessel', 'bw', 'ch', 'bs', 'b', 'c'],
                        help='Filter type (alternative to positional)')
    parser.add_argument('-f', '--freq', dest='freq_flag',
                        help='Cutoff frequency (alternative to positional)')

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

    # New output options
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Output only component values (no header/diagram)')
    parser.add_argument('--format', choices=['table', 'json', 'csv'],
                        default='table', help='Output format (default: table)')

    args = parser.parse_args()

    # Merge positional and flag arguments
    filter_type = args.filter_type or args.type_flag
    freq_input = args.frequency or args.freq_flag

    if args.explain:
        if not filter_type:
            parser.error('Filter type required for --explain')
        resolved_type = resolve_filter_type(filter_type)
        if resolved_type == 'butterworth':
            print(BUTTERWORTH_EXPLANATION)
        elif resolved_type == 'chebyshev':
            print(CHEBYSHEV_EXPLANATION)
        else:
            print(BESSEL_EXPLANATION)
        sys.exit(0)

    if not filter_type:
        parser.error('Filter type required (positional or -t/--type)')
    if not freq_input:
        parser.error('Frequency required (positional or -f/--freq)')

    filter_type = resolve_filter_type(filter_type)

    try:
        freq_hz = parse_frequency(freq_input)
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

    if filter_type == 'butterworth':
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
    elif filter_type == 'chebyshev':
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
    else:  # bessel
        capacitors, inductors, order = calculate_bessel(freq_hz, impedance, args.components)
        result = {
            'filter_type': 'bessel',
            'freq_hz': freq_hz,
            'impedance': impedance,
            'capacitors': capacitors,
            'inductors': inductors,
            'order': order,
            'ripple': None,
        }

    display_results(result, raw=args.raw, output_format=args.format, quiet=args.quiet)


if __name__ == '__main__':
    main()
