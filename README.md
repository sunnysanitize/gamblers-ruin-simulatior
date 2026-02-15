# Gambler's Ruin Simulation

Monte Carlo + closed-form gambler's ruin analysis with an interactive Flask UI.

## Features

- Runs Monte Carlo experiments up to `100,000` trials.
- Compares empirical `P(reach goal)` with closed-form theoretical probability.
- Visualizes:
  - probability convergence over sample size
  - absolute empirical-vs-theory error (with 1%-2% guide bands)
  - variance decay of the estimator as trials increase
  - sample bankroll paths and outcome durations
- Flask interface supports dynamic parameter experimentation and target-goal configuration sweeps.

## Run (CLI + Flask)

```bash
cd /Users/ricedevice/gamblers-ruin-simulation
python3 -m pip install -r requirements.txt
python3 gamblersruin.py --trials 20000 --paths 20
```

This will:
- generate `gamblers_ruin_dashboard.html`
- print empirical vs theoretical probability and absolute error
- start an interactive Flask server at `http://127.0.0.1:5000`
- open your browser automatically

## Useful options

```bash
python3 gamblersruin.py --trials 100000
python3 gamblersruin.py --target-goals 40,50,60
python3 gamblersruin.py --no-open-browser
python3 gamblersruin.py --host 127.0.0.1 --port 5050
python3 gamblersruin.py --no-serve
```
