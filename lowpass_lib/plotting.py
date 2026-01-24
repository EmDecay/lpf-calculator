"""
ASCII plotting and data export for filter frequency response.

Provides visualization of filter magnitude response and export to JSON/CSV.
"""

import json
import math


def _format_freq_compact(freq_hz: float) -> str:
    """Format frequency compactly for plot labels."""
    if freq_hz >= 1e9:
        return f"{freq_hz/1e9:.3g}G"
    elif freq_hz >= 1e6:
        return f"{freq_hz/1e6:.3g}M"
    elif freq_hz >= 1e3:
        return f"{freq_hz/1e3:.3g}k"
    else:
        return f"{freq_hz:.3g}"


def generate_frequency_points(cutoff_hz: float, num_points: int = 51) -> list[float]:
    """
    Generate logarithmically-spaced frequency points from 0.1fc to 10fc.

    Args:
        cutoff_hz: Cutoff frequency in Hz
        num_points: Number of points to generate (default 51 for smooth curves)

    Returns:
        List of frequencies in Hz spanning 2 decades centered on cutoff
    """
    if cutoff_hz <= 0:
        raise ValueError("Cutoff frequency must be positive")
    if num_points < 2:
        raise ValueError("Need at least 2 points")

    # Generate points from 10^-1 to 10^1 relative to cutoff (2 decades)
    points = []
    for i in range(num_points):
        # Linear interpolation from -1 to 1 in log space
        exp = -1 + (2 * i / (num_points - 1))
        points.append(cutoff_hz * (10 ** exp))
    return points


def _find_3db_frequency(freqs: list[float], response_db: list[float]) -> float | None:
    """Find frequency where response crosses -3dB threshold."""
    for i in range(len(response_db) - 1):
        if response_db[i] >= -3 and response_db[i + 1] < -3:
            # Linear interpolation between points
            if response_db[i] == response_db[i + 1]:
                return freqs[i]
            ratio = (-3 - response_db[i]) / (response_db[i + 1] - response_db[i])
            # Log interpolation for frequency
            log_f1, log_f2 = math.log10(freqs[i]), math.log10(freqs[i + 1])
            return 10 ** (log_f1 + ratio * (log_f2 - log_f1))
    return None


def render_ascii_plot(freqs: list[float], response_db: list[float],
                      cutoff_hz: float, width: int = 60, height: int = 12) -> str:
    """
    Render ASCII frequency response plot.

    Args:
        freqs: List of frequencies in Hz
        response_db: List of magnitude responses in dB
        cutoff_hz: Cutoff frequency for axis labeling
        width: Plot width in characters (default 60)
        height: Plot height in lines (default 12)

    Returns:
        Multi-line string containing the ASCII plot
    """
    if len(freqs) != len(response_db):
        raise ValueError("Frequency and response lists must have same length")
    if width < 40:
        width = 40  # Minimum width for readability
    if height < 6:
        height = 6  # Minimum height

    # dB range: 0 to -60 (or min of data, whichever is less negative)
    db_max = 0
    db_min = max(-60, min(response_db) - 5)  # Leave some margin

    # Frequency range in log space
    freq_min = min(freqs)
    freq_max = max(freqs)
    log_min = math.log10(freq_min)
    log_max = math.log10(freq_max)

    # Guard against identical frequencies (division by zero)
    log_range = log_max - log_min
    if log_range == 0:
        log_range = 1.0  # Fallback for single frequency

    # Guard against flat dB response (division by zero)
    db_range = db_max - db_min
    if db_range == 0:
        db_range = 1.0  # Fallback for flat response

    # Build the plot grid
    plot_width = width - 8  # Leave room for axis labels
    plot_height = height - 2  # Leave room for x-axis labels

    # Initialize grid with spaces
    grid = [[' ' for _ in range(plot_width)] for _ in range(plot_height)]

    # Find -3dB row position for reference line
    db_3db_row = int((db_max - (-3)) / db_range * (plot_height - 1))
    db_3db_row = max(0, min(plot_height - 1, db_3db_row))

    # Find -3dB frequency for annotation
    f_3db = _find_3db_frequency(freqs, response_db)
    f_3db_col = None
    # Only mark -3dB if it differs significantly from cutoff (>1%)
    show_3db_marker = False
    if f_3db and f_3db > 0:
        log_f_3db = math.log10(f_3db)
        f_3db_col = int((log_f_3db - log_min) / log_range * (plot_width - 1))
        f_3db_col = max(0, min(plot_width - 1, f_3db_col))
        show_3db_marker = abs(f_3db - cutoff_hz) / cutoff_hz > 0.01

    # Draw -3dB reference line (dashed)
    for col in range(plot_width):
        if grid[db_3db_row][col] == ' ':
            grid[db_3db_row][col] = '·' if col % 2 == 0 else ' '

    # Plot the response curve
    for freq, db in zip(freqs, response_db):
        # Map frequency to column (log scale)
        if freq <= 0:
            continue
        log_freq = math.log10(freq)
        col = int((log_freq - log_min) / log_range * (plot_width - 1))
        col = max(0, min(plot_width - 1, col))

        # Map dB to row (0 dB at top, db_min at bottom)
        row = int((db_max - db) / db_range * (plot_height - 1))
        row = max(0, min(plot_height - 1, row))

        # Fill from this point down to show area under curve
        for r in range(row, plot_height):
            grid[r][col] = '█'

    # Mark -3dB crossing point (only when it differs from cutoff)
    if show_3db_marker and f_3db_col is not None:
        grid[db_3db_row][f_3db_col] = '●'

    # Build output string
    lines = []
    lines.append("Frequency Response (dB)")
    lines.append("")

    # Add rows with dB labels
    for row_idx in range(plot_height):
        # Calculate dB value for this row
        db_val = db_max - (row_idx / (plot_height - 1)) * (db_max - db_min)

        # Label -3dB row specially, otherwise label key rows
        if row_idx == db_3db_row:
            label = "   -3 │"
        elif row_idx == 0:
            label = f"{db_val:5.0f} │"
        elif row_idx == plot_height - 1:
            label = f"{db_min:5.0f} │"
        elif row_idx == plot_height // 2 and abs(row_idx - db_3db_row) > 1:
            mid_db = (db_max + db_min) / 2
            label = f"{mid_db:5.0f} │"
        else:
            label = "      │"

        lines.append(label + ''.join(grid[row_idx]))

    # X-axis with tick marks at decade subdivisions
    x_axis = list("─" * plot_width)

    # Add tick marks at 2x, 5x, and 10x intervals within each decade
    tick_multipliers = [1, 2, 5]
    for decade in range(-1, 2):  # 0.1x to 10x cutoff
        for mult in tick_multipliers:
            tick_freq = cutoff_hz * mult * (10 ** decade)
            if freq_min <= tick_freq <= freq_max:
                log_tick = math.log10(tick_freq)
                tick_col = int((log_tick - log_min) / log_range * (plot_width - 1))
                if 0 <= tick_col < plot_width:
                    x_axis[tick_col] = '┼'

    # Add arrow at -3dB frequency (only when it differs from cutoff)
    if show_3db_marker and f_3db_col is not None and 0 <= f_3db_col < plot_width:
        x_axis[f_3db_col] = '▲'

    lines.append("      +" + ''.join(x_axis))

    # Frequency labels
    low_freq = cutoff_hz * 0.1
    high_freq = cutoff_hz * 10
    low_label = _format_freq_compact(low_freq)
    high_label = _format_freq_compact(high_freq)

    # Cutoff frequency position and label
    fc_col = int((math.log10(cutoff_hz) - log_min) / log_range * plot_width)
    fc_label = _format_freq_compact(cutoff_hz) + "(fc)"

    # Build label line with low, cutoff, and high frequencies
    freq_label = " " * 6 + " "  # Align with plot
    freq_label += low_label
    freq_label += " " * max(0, fc_col - len(low_label) - len(fc_label) // 2) + fc_label
    freq_label += " " * max(0, plot_width - fc_col - len(fc_label) // 2 - len(high_label)) + high_label
    lines.append(freq_label)

    # Add second label line for -3dB frequency when it differs from cutoff
    if show_3db_marker and f_3db:
        f3_label = _format_freq_compact(f_3db) + "(-3dB)"
        f3_col = f_3db_col if f_3db_col else plot_width // 2
        # Build line with just the -3dB label positioned correctly
        f3_line = " " * 7  # Align with plot
        f3_line += " " * f3_col + "▲" + f3_label
        lines.append(f3_line)

    return '\n'.join(lines)


def export_response_json(freqs: list[float], response_db: list[float],
                         filter_info: dict) -> str:
    """
    Export frequency response data as JSON.

    Args:
        freqs: List of frequencies in Hz (full precision preserved)
        response_db: List of magnitude responses in dB (rounded to 2 decimals)
        filter_info: Dict with filter_type, cutoff_hz, order, and optionally ripple

    Returns:
        JSON string with filter info and response data
    """
    output = {
        'filter_type': filter_info.get('filter_type', 'unknown'),
        'cutoff_hz': filter_info.get('cutoff_hz') or filter_info.get('freq_hz', 0),
        'order': filter_info.get('order', 0),
        'data': [
            {'frequency_hz': f, 'magnitude_db': round(db, 2)}
            for f, db in zip(freqs, response_db)
        ]
    }

    if 'ripple' in filter_info and filter_info['ripple'] is not None:
        output['ripple_db'] = filter_info['ripple']

    return json.dumps(output, indent=2)


def export_response_csv(freqs: list[float], response_db: list[float]) -> str:
    """
    Export frequency response data as CSV.

    Args:
        freqs: List of frequencies in Hz
        response_db: List of magnitude responses in dB

    Returns:
        CSV string with frequency and magnitude columns
    """
    lines = ['frequency_hz,magnitude_db']
    for f, db in zip(freqs, response_db):
        lines.append(f'{f:.6g},{db:.2f}')
    return '\n'.join(lines)
