"""
ASCII plotting and data export for filter frequency response.

Provides visualization of filter magnitude response and export to JSON/CSV.
"""

import json
import math


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

    # Build output string
    lines = []
    lines.append("Frequency Response (dB)")
    lines.append("")

    # Add rows with dB labels
    for row_idx in range(plot_height):
        # Calculate dB value for this row
        db_val = db_max - (row_idx / (plot_height - 1)) * (db_max - db_min)

        # Label every few rows
        if row_idx == 0:
            label = f"{db_val:5.0f} │"
        elif row_idx == plot_height - 1:
            label = f"{db_min:5.0f} │"
        elif row_idx == plot_height // 2:
            mid_db = (db_max + db_min) / 2
            label = f"{mid_db:5.0f} │"
        else:
            label = "      │"

        lines.append(label + ''.join(grid[row_idx]))

    # X-axis
    lines.append("      +" + "─" * plot_width)

    # Frequency labels
    fc_col = int((math.log10(cutoff_hz) - log_min) / log_range * plot_width)
    freq_label = " " * 6 + " "  # Align with plot
    freq_label += "0.1fc"
    freq_label += " " * max(0, fc_col - 10) + "fc"
    freq_label += " " * max(0, plot_width - fc_col - 8) + "10fc"
    lines.append(freq_label)

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
