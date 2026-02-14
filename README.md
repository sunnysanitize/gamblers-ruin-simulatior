# Gambler's Ruin Simulation

## Run the browser app (recommended)

```bash
cd /Users/ricedevice/gamblers-ruin-simulation
python3 -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit will print a local URL (usually `http://localhost:8501`) and open it in your browser.

## Run CLI mode

```bash
python3 gamblersruin.py --trials 10000 --paths 30 --open-browser
```

This generates `gamblers_ruin_dashboard.html`.
