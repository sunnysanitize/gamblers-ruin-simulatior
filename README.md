# Gambler's Ruin Simulation

## Run with Flask dashboard (recommended)

```bash
cd /Users/ricedevice/gamblers-ruin-simulation
python3 -m pip install -r requirements.txt
python3 gamblersruin.py --trials 10000 --paths 30
```

This will:
- generate `gamblers_ruin_dashboard.html`
- start a Flask server at `http://127.0.0.1:5000`
- open your browser automatically

## Useful options

```bash
python3 gamblersruin.py --no-open-browser
python3 gamblersruin.py --host 127.0.0.1 --port 5050
python3 gamblersruin.py --no-serve
```
