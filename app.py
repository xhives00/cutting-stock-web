from flask import Flask, render_template, request
from solver import solve_cutting_stock

app = Flask(__name__)

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/solve")
def solve():
    # 1) načítaj vstupy
    stock_length_raw = request.form.get("stock_length", "").strip()
    items_raw = request.form.get("items", "").strip()
    kerf_raw = request.form.get("kerf", "").strip()

    # 2) validácia (super dôležité bez loginu)
    try:
        stock_length = int(stock_length_raw)
        if stock_length <= 0 or stock_length > 100000:
            raise ValueError()
    except ValueError:
        return render_template("index.html", error="Stock length musí byť kladné celé číslo (rozumný rozsah).")

    # items vo formáte napr:
    # 1200x20
    # 2400x10
    # 900x9
    # 800x3
    items = []
    if not items_raw:
        return render_template("index.html", error="Zadaj aspoň 1 položku (napr. 1200x20).")

    lines = [ln.strip() for ln in items_raw.splitlines() if ln.strip()]
    if len(lines) > 200:
        return render_template("index.html", error="Príliš veľa riadkov (limit 200).")

    try:
        for ln in lines:
            # povolíme aj 1200 20 alebo 1200x20
            if "x" in ln.lower():
                a, b = ln.lower().split("x", 1)
            else:
                a, b = ln.split(None, 1)
            length = int(a.strip())
            count = int(b.strip())
            if length <= 0 or count <= 0:
                raise ValueError()
            items.append((length, count))
    except Exception:
        return render_template("index.html", error="Zlý formát. Použi riadky ako 1200x20 alebo '1200 20'.")

    try:
        kerf = int(kerf_raw)
        if kerf < 0 or kerf > 50:
            raise ValueError()
    except ValueError:
        return render_template("index.html", error="Kerf musí byť celé číslo 0–50 mm.")
    
    # 3) zavolaj solver
    result = solve_cutting_stock(stock_length, items, kerf)

    # 4) ukáž výsledok
    return render_template("result.html", stock_length=stock_length, items=items, result=result)

if __name__ == "__main__":
    app.run(debug=True)
