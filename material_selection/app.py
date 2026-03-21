from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# ✅ Safe path for materials.csv (works everywhere)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "materials.csv")

# Load data safely
try:
    data = pd.read_csv(file_path)
except Exception as e:
    print("CSV Load Error:", e)
    data = pd.DataFrame(columns=["Material", "Strength", "Density", "Temperature"])


# ✅ Material Ranking Function (Filtering + Ranking)
def rank_materials(df, strength_req, density_req, temp_req):

    # Apply filtering
    filtered = df[
        (df["Strength"] >= strength_req) &
        (df["Density"] <= density_req) &
        (df["Temperature"] >= temp_req)
    ].copy()

    # If no match → fallback
    if filtered.empty:
        filtered = df.copy()

    # Score calculation
    filtered["Score"] = (
        (filtered["Strength"] / strength_req) * 0.5 +
        (density_req / filtered["Density"]) * 0.3 +
        (filtered["Temperature"] / temp_req) * 0.2
    )

    return filtered.sort_values(by="Score", ascending=False)


@app.route("/", methods=["GET", "POST"])
def index():

    results = None

    # ✅ Prevent chart crash
    chart_data = {
        "labels": [],
        "strength": [],
        "density": [],
        "temperature": []
    }

    if request.method == "POST":
        try:
            strength = float(request.form["strength"])
            density = float(request.form["density"])
            temperature = float(request.form["temperature"])

            ranked = rank_materials(data.copy(), strength, density, temperature)
            results = ranked.head(5)

            # Chart data
            chart_data = {
                "labels": list(results["Material"]),
                "strength": list(results["Strength"]),
                "density": list(results["Density"]),
                "temperature": list(results["Temperature"])
            }

        except Exception as e:
            print("INPUT ERROR:", e)

    return render_template("index.html", tables=results, chart_data=chart_data)


# ✅ Required for Render deployment
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
