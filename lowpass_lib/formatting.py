"""
Output formatting for Pi LC low-pass filters.

Contains unit formatters and display functions for filter results.
"""


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


def display_results(result: dict, raw: bool = False) -> None:
    """
    Display calculated filter component values.

    Args:
        result: Dict containing filter calculation results with keys:
            - filter_type: 'butterworth' or 'chebyshev'
            - freq_hz: Cutoff frequency in Hz
            - impedance: Characteristic impedance in Ohms
            - capacitors: List of capacitor values in Farads
            - inductors: List of inductor values in Henries
            - order: Filter order
            - ripple: Passband ripple in dB (Chebyshev only)
        raw: If True, display values in scientific notation
    """
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

    # Component values table
    max_rows = max(n_caps, n_inds)
    col_width = 24

    print(f"\n{'Component Values':^50}")
    print(f"+{'-' * col_width}+{'-' * col_width}+")
    print(f"|{'Capacitors':^{col_width}}|{'Inductors':^{col_width}}|")
    print(f"+{'-' * col_width}+{'-' * col_width}+")

    for i in range(max_rows):
        if i < n_caps:
            val = result['capacitors'][i]
            if raw:
                cap_str = f"C{i+1}: {val:.6e} F"
            else:
                cap_str = f"C{i+1}: {format_capacitance(val)}"
        else:
            cap_str = ""

        if i < n_inds:
            val = result['inductors'][i]
            if raw:
                ind_str = f"L{i+1}: {val:.6e} H"
            else:
                ind_str = f"L{i+1}: {format_inductance(val)}"
        else:
            ind_str = ""

        print(f"| {cap_str:<{col_width-2}} | {ind_str:<{col_width-2}} |")

    print(f"+{'-' * col_width}+{'-' * col_width}+")
    print()
