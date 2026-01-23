# Pi LC Low Pass Filter Calculator

Command-line tool for calculating component values for Pi-topology LC low-pass filters.

Written by Matt N3AR (with AI coding assistance)

## Usage

```bash
./pi-lowpass-filter.py <type> <frequency> [options]
```

### Butterworth Filter

Maximally-flat frequency response. Best when you need the smoothest passband and can tolerate a gentler rolloff.

```bash
./pi-lowpass-filter.py bw 10MHz -n 5
```

### Chebyshev Filter

Configurable passband ripple. Best when you need a sharp cutoff and can accept some ripple in the passband.

```bash
./pi-lowpass-filter.py ch 100MHz -r 0.5 -n 5
```

### Bessel Filter

Maximally-flat group delay (linear phase). Best for pulse/transient applications where waveform preservation matters more than sharp cutoff.

```bash
./pi-lowpass-filter.py bs 10MHz -n 5
```

### Output Formats

```bash
# JSON output (for scripting)
./pi-lowpass-filter.py bw 10MHz --format json

# CSV output (for spreadsheets)
./pi-lowpass-filter.py bw 10MHz --format csv

# Quiet mode (values only)
./pi-lowpass-filter.py bw 10MHz -q
```

## Options

| Option | Description |
|--------|-------------|
| `type` | Filter type: `butterworth`/`bw`, `chebyshev`/`ch`, or `bessel`/`bs` (positional) |
| `frequency` | Cutoff frequency (e.g., 10MHz, 1.5GHz) (positional) |
| `-t, --type` | Filter type (flag alternative to positional) |
| `-f, --freq` | Cutoff frequency (flag alternative to positional) |
| `-z, --impedance` | Characteristic impedance, default 50 ohms |
| `-n, --components` | Number of components/poles: 2-9 (default: 3) |
| `-r, --ripple` | Passband ripple in dB, Chebyshev only (default: 0.5) |
| `-q, --quiet` | Output only component values (no header/diagram) |
| `--format` | Output format: `table` (default), `json`, or `csv` |
| `--raw` | Output raw values in Farads and Henries |
| `--explain` | Explain how the selected filter type works |

## Example Output

```
Butterworth Pi Low Pass Filter
==================================================
Cutoff Frequency:    10 MHz
Impedance Z0:        50 Ohm
Order:               5
==================================================

Topology:
  IN ───┬───┤ L1 ├───┬───┤ L2 ├───┬─── OUT
        │            │            │
       ===          ===          ===
       C1           C2           C3
        │            │            │
       GND          GND          GND

                 Component Values
+------------------------+------------------------+
|       Capacitors       |       Inductors        |
+------------------------+------------------------+
| C1: 196.73 pF          | L1: 1.29 uH            |
| C2: 636.62 pF          | L2: 1.29 uH            |
| C3: 196.73 pF          |                        |
+------------------------+------------------------+
```

## Pi Topology

Capacitors are shunt elements (to ground), inductors are series elements (in the signal path). The number of components equals the filter order (poles). The topology diagram is dynamically generated based on the number of components.

## Project Structure

```
lpf-calculator/
├── pi-lowpass-filter.py    # Main CLI entry point
├── lowpass_lib/            # Filter calculation library
│   ├── __init__.py         # Package exports
│   ├── calculations.py     # Butterworth, Chebyshev & Bessel formulas
│   ├── formatting.py       # Output formatting & topology diagrams
│   └── parsing.py          # Frequency & impedance parsing
└── README.md
```

## Requirements

Python 3.9+ (uses generic type hint syntax)

## License

MIT

## Author

Matt N3AR (with AI coding assistance)
