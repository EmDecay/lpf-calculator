"""
Pi LC Low Pass Filter Library.

Provides calculations, parsing, and formatting for Butterworth, Chebyshev,
and Bessel Pi-topology low-pass filters.
"""

from .calculations import (
    calculate_butterworth,
    calculate_chebyshev,
    calculate_bessel,
)
from .formatting import (
    format_frequency,
    format_capacitance,
    format_inductance,
    format_json,
    format_csv,
    format_quiet,
    display_results,
)
from .parsing import (
    parse_frequency,
    parse_impedance,
)
from .eseries import (
    E12_VALUES,
    E24_VALUES,
    E96_VALUES,
    MatchResult,
    get_eseries_values,
    normalize_to_decade,
    find_closest,
    find_parallel_match,
    match_component,
)
from .transfer import (
    butterworth_response,
    chebyshev_response,
    bessel_response,
    chebyshev_polynomial,
    magnitude_to_db,
    frequency_response,
)
from .plotting import (
    generate_frequency_points,
    render_ascii_plot,
    export_response_json,
    export_response_csv,
)

__all__ = [
    'calculate_butterworth',
    'calculate_chebyshev',
    'calculate_bessel',
    'format_frequency',
    'format_capacitance',
    'format_inductance',
    'format_json',
    'format_csv',
    'format_quiet',
    'display_results',
    'parse_frequency',
    'parse_impedance',
    'E12_VALUES',
    'E24_VALUES',
    'E96_VALUES',
    'MatchResult',
    'get_eseries_values',
    'normalize_to_decade',
    'find_closest',
    'find_parallel_match',
    'match_component',
    'butterworth_response',
    'chebyshev_response',
    'bessel_response',
    'chebyshev_polynomial',
    'magnitude_to_db',
    'frequency_response',
    'generate_frequency_points',
    'render_ascii_plot',
    'export_response_json',
    'export_response_csv',
]
