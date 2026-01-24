"""
Output formatting for Pi LC low-pass filters.

Contains unit formatters and display functions for filter results.
"""

import csv
import io
import json

from .eseries import match_component
from .transfer import frequency_response
from .plotting import generate_frequency_points, render_ascii_plot


def _format_with_units(value: float, units: list[tuple[float, str]], precision: str = ".4g") -> str:
    """Generic formatter for values with unit suffixes."""
    for threshold, suffix in units:
        if abs(value) >= threshold:
            return f"{value/threshold:{precision}} {suffix}"
    # Use last unit if value is smaller than all thresholds
    _, suffix = units[-1]
    return f"{value/units[-1][0]:{precision}} {suffix}"


def format_frequency(freq_hz: float) -> str:
    """Format frequency with appropriate unit (GHz, MHz, kHz, Hz)."""
    return _format_with_units(freq_hz, [
        (1e9, 'GHz'), (1e6, 'MHz'), (1e3, 'kHz'), (1, 'Hz')
    ])


def format_capacitance(value_farads: float) -> str:
    """Format capacitance with appropriate unit (mF, uF, nF, pF)."""
    return _format_with_units(value_farads, [
        (1e-3, 'mF'), (1e-6, 'uF'), (1e-9, 'nF'), (1e-12, 'pF')
    ], ".2f")


def format_inductance(value_henries: float) -> str:
    """Format inductance with appropriate unit (H, mH, uH, nH)."""
    return _format_with_units(value_henries, [
        (1, 'H'), (1e-3, 'mH'), (1e-6, 'uH'), (1e-9, 'nH')
    ], ".2f")


def format_json(result: dict) -> str:
    """Format results as JSON."""
    output = {
        'filter_type': result['filter_type'],
        'cutoff_frequency_hz': result['freq_hz'],
        'impedance_ohms': result['impedance'],
        'order': result['order'],
        'components': {
            'capacitors': [{'name': f'C{i+1}', 'value_farads': v}
                          for i, v in enumerate(result['capacitors'])],
            'inductors': [{'name': f'L{i+1}', 'value_henries': v}
                         for i, v in enumerate(result['inductors'])]
        }
    }
    if result.get('ripple'):
        output['ripple_db'] = result['ripple']
    return json.dumps(output, indent=2)


def format_csv(result: dict) -> str:
    """Format results as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Component', 'Value', 'Unit'])
    for i, v in enumerate(result['capacitors']):
        formatted = format_capacitance(v)
        val, unit = formatted.rsplit(' ', 1)
        writer.writerow([f'C{i+1}', val, unit])
    for i, v in enumerate(result['inductors']):
        formatted = format_inductance(v)
        val, unit = formatted.rsplit(' ', 1)
        writer.writerow([f'L{i+1}', val, unit])
    return output.getvalue()


def format_quiet(result: dict, raw: bool = False) -> str:
    """Format results as minimal text (values only)."""
    lines = []
    for i, v in enumerate(result['capacitors']):
        if raw:
            lines.append(f"C{i+1}: {v:.6e} F")
        else:
            lines.append(f"C{i+1}: {format_capacitance(v)}")
    for i, v in enumerate(result['inductors']):
        if raw:
            lines.append(f"L{i+1}: {v:.6e} H")
        else:
            lines.append(f"L{i+1}: {format_inductance(v)}")
    return '\n'.join(lines)


def _print_pi_topology_diagram(n_capacitors: int, n_inductors: int) -> None:
    """
    Print dynamic Pi topology diagram for low-pass filter.

    Pi topology: shunt capacitors to ground, series inductors in signal path.
    C1 - L1 - C2 - L2 - C3 ... Cn

    Args:
        n_capacitors: Number of shunt capacitors
        n_inductors: Number of series inductors
    """
    # Calculate segment width based on components
    # Each segment: capacitor position + inductor between
    seg_w = 14  # Width for each segment (───┤ L1 ├───┬)

    # Build main line with inductors and capacitor tap points
    # Pattern: IN ───┬───┤ L1 ├───┬───┤ L2 ├───┬─── OUT
    main_parts = ["  IN ───┬"]

    for i in range(n_inductors):
        main_parts.append(f"───┤ L{i+1} ├───┬")

    # Handle last capacitor (no inductor after it)
    if n_capacitors > n_inductors:
        main_parts.append("─── OUT")
    else:
        # Replace last ┬ with direct output
        main_parts[-1] = main_parts[-1][:-1] + "─── OUT"

    main_line = "".join(main_parts)
    line_len = len(main_line)

    # Calculate capacitor tap positions (at ┬ characters)
    cap_positions = []
    pos = main_line.find('┬')
    while pos != -1:
        cap_positions.append(pos)
        pos = main_line.find('┬', pos + 1)

    def build_line(positions: list[int], elements: list[str]) -> str:
        """Build line with elements centered at given positions."""
        chars = [' '] * line_len
        for pos, elem in zip(positions, elements):
            start = pos - len(elem) // 2
            for j, ch in enumerate(elem):
                if 0 <= start + j < line_len:
                    chars[start + j] = ch
        return ''.join(chars)

    # Build vertical lines from main to capacitors
    vert_line = build_line(cap_positions, ['│'] * n_capacitors)

    # Capacitor symbols (===)
    cap_sym = build_line(cap_positions, ['==='] * n_capacitors)

    # Capacitor labels
    cap_labels = [f"C{i+1}" for i in range(n_capacitors)]
    label_line = build_line(cap_positions, cap_labels)

    # Ground connections
    gnd_wire = build_line(cap_positions, ['│'] * n_capacitors)
    gnd_sym = build_line(cap_positions, ['GND'] * n_capacitors)

    print(main_line)
    print(vert_line)
    print(cap_sym)
    print(label_line)
    print(gnd_wire)
    print(gnd_sym)


def display_results(result: dict, raw: bool = False,
                    output_format: str = 'table', quiet: bool = False,
                    eseries: str = 'E24', show_match: bool = True,
                    show_plot: bool = False) -> None:
    """
    Display calculated filter component values.

    Args:
        result: Dict containing filter calculation results
        raw: If True, display values in scientific notation
        output_format: 'table', 'json', or 'csv'
        quiet: If True, output only component values (no header/diagram)
        eseries: E-series for component matching (E12, E24, E96)
        show_match: If True, show E-series component suggestions
        show_plot: If True, show ASCII frequency response plot
    """
    if output_format == 'json':
        print(format_json(result))
        return
    if output_format == 'csv':
        print(format_csv(result), end='')
        return
    if quiet:
        print(format_quiet(result, raw))
        return

    title = f"{result['filter_type'].title()} Pi Low Pass Filter"

    print(f"\n{title}")
    print("=" * 50)
    print(f"Cutoff Frequency:    {format_frequency(result['freq_hz'])}")
    print(f"Impedance Z0:        {result['impedance']:.4g} Ohm")
    if result.get('ripple') is not None:
        print(f"Ripple:              {result['ripple']} dB")
    print(f"Order:               {result['order']}")
    print("=" * 50)

    # Topology diagram
    n_caps = len(result['capacitors'])
    n_inds = len(result['inductors'])

    print("\nTopology:")
    _print_pi_topology_diagram(n_caps, n_inds)

    # Component values table with E-series matching
    max_rows = max(n_caps, n_inds)
    col_width = 28 if show_match else 24

    print(f"\n{'Component Values':^58}")
    print(f"+{'-' * col_width}+{'-' * col_width}+")
    print(f"|{'Capacitors':^{col_width}}|{'Inductors':^{col_width}}|")
    print(f"+{'-' * col_width}+{'-' * col_width}+")

    for i in range(max_rows):
        # Capacitor column
        if i < n_caps:
            val = result['capacitors'][i]
            if raw:
                cap_str = f"C{i+1}: {val:.6e} F"
            else:
                cap_str = f"C{i+1}: {format_capacitance(val)}"
        else:
            cap_str = ""

        # Inductor column
        if i < n_inds:
            val = result['inductors'][i]
            if raw:
                ind_str = f"L{i+1}: {val:.6e} H"
            else:
                ind_str = f"L{i+1}: {format_inductance(val)}"
        else:
            ind_str = ""

        print(f"| {cap_str:<{col_width-2}} | {ind_str:<{col_width-2}} |")

        # E-series matching row (show warning for >10% error)
        if show_match and not raw:
            cap_match_str = ""
            ind_match_str = ""

            if i < n_caps:
                match = match_component(result['capacitors'][i], eseries)
                warn = "!" if abs(match.error_percent) > 10 else ""
                cap_match_str = f"  -> {format_capacitance(match.matched_value)} ({match.error_percent:+.1f}%){warn}"

            if i < n_inds:
                match = match_component(result['inductors'][i], eseries)
                warn = "!" if abs(match.error_percent) > 10 else ""
                ind_match_str = f"  -> {format_inductance(match.matched_value)} ({match.error_percent:+.1f}%){warn}"

            if cap_match_str or ind_match_str:
                print(f"| {cap_match_str:<{col_width-2}} | {ind_match_str:<{col_width-2}} |")

    print(f"+{'-' * col_width}+{'-' * col_width}+")

    # Frequency response plot
    if show_plot:
        freqs = generate_frequency_points(result['freq_hz'])
        ripple = result.get('ripple') or 0.5
        response = frequency_response(result['filter_type'], freqs, result['freq_hz'],
                                       result['order'], ripple)
        print()
        print(render_ascii_plot(freqs, response, result['freq_hz']))

    print()
