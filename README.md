# 1D Cutting Stock – Flask Web App

Simple Flask web application that exposes a Python-based heuristic solver for the 1D cutting stock problem.

The app allows users to input stock length, kerf width, and required piece lengths with counts, and returns a cutting plan optimized primarily for minimal waste.

No authentication, no database – intended as a lightweight demo / utility for friends and experimentation.

---

## Features

- Python heuristic solver (backtracking + pruning)
- Web interface built with Flask
- No login, no persistence
- Designed for low-traffic usage on free hosting
- JSON-based internal results, easy to extend

---

## Input Format

- **Stock length**: integer (mm)
- **Kerf**: integer (mm)
- **Pieces**: one per line, format:
    1200x20
    2400x10
    900x9
    800x3

---

## Running Locally

bash:
pip install -r requirements.txt
python app.py
Then open:
http://127.0.0.1:5000

---

## Notes

Solver uses heuristics, not guaranteed global optimum

Input size is intentionally limited to prevent excessive computation

Intended for educational and practical use, not safety-critical applications