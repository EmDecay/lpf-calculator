# Pi LC Low Pass Filter Calculator

Command-line tool for calculating component values for Pi-topology LC low-pass filters.

Written by Matt N3AR (with AI coding assistance)

## Usage

```bash
./pi-lowpass-filter.py -t <type> -f <frequency> [options]
```

### Butterworth Filter

Maximally-flat frequency response. Best when you need the smoothest passband and can tolerate a gentler rolloff.

```bash
./pi-lowpass-filter.py -t butterworth -f 10MHz -z 50 -n 5
```

### Chebyshev Filter

Configurable passband ripple. Best when you need a sharp cutoff and can accept some ripple in the passband.

```bash
./pi-lowpass-filter.py -t chebyshev -f 100MHz -z 50 -r 0.5 -n 5
```

## Options

| Option | Description |
|--------|-------------|
| `-t, --type` | Filter type: `butterworth` or `chebyshev` (required) |
| `-f, --frequency` | Cutoff frequency (e.g., 100MHz, 1.5GHz, 500kHz) |
| `-z, --impedance` | Characteristic impedance, default 50 ohms |
| `-n, --components` | Number of components/poles: 2-9 (default: 3) |
| `-r, --ripple` | Passband ripple in dB, Chebyshev only (default: 0.5) |
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
│   ├── calculations.py     # Butterworth & Chebyshev formulas
│   ├── formatting.py       # Output formatting & topology diagrams
│   └── parsing.py          # Frequency & impedance parsing
└── README.md
```

## Requirements

Python 3.9+ (uses generic type hint syntax)

## License

MIT
