# LC Low Pass Filter Calculators

Command-line tools for calculating component values for Pi-topology LC low-pass filters.

Written by Matt N3AR (with AI coding assistance)

## Calculators

### Butterworth Pi Low Pass Filter

Calculates component values for maximally-flat frequency response. Best when you need the smoothest passband and can tolerate a gentler rolloff.

```bash
./butterworth-pi-lowpass-filter.py -f 10MHz -z 50 -n 5
```

Options:
- `-f, --frequency` - Cutoff frequency (e.g., 100MHz, 1.5GHz, 500kHz)
- `-z, --impedance` - Characteristic impedance, default 50 ohms
- `-n, --components` - Number of components 1-11, default 3
- `--raw` - Output raw values in Farads and Henries
- `--explain` - Explain how this filter works

### Chebyshev Pi Low Pass Filter

Calculates component values with configurable passband ripple. Best when you need a sharp cutoff and can accept some ripple in the passband.

```bash
./chebyshev-pi-lowpass-filter.py -f 100MHz -z 50 -r 0.5 -n 5
```

Options:
- `-f, --freq` - Cutoff frequency (e.g., 100MHz, 1.5GHz, 14200000)
- `-z, --impedance` - Characteristic impedance in ohms
- `-r, --ripple` - Passband ripple in dB (e.g., 0.5, 0.1)
- `-n, --order` - Number of components 1-11 (adjusted to odd for Pi topology)
- `--explain` - Explain how this filter works

## Pi Topology

Both calculators output values for Pi-topology filters:

```
        ┌──────┤ L1 ├──────┬──────┤ L2 ├──────┐
  IN ───┤                  │                  ├─── OUT
       ===C1              ===C2              ===C3
        │                  │                  │
       GND                GND                GND
```

Capacitors are shunt elements (to ground), inductors are series elements (in the signal path).

## Requirements

Python 3.10+ (uses type hint syntax)

## License

MIT
