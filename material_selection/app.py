from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# Load CSV safely
try:
    data = pd.read_csv("materials.csv")
except:
    data = pd.DataFrame(columns=["Material","Strength","Density","Temperature"])

def rank_materials(df, strength_req, density_req, temp_req):

    filtered = df[
        (df["Strength"] >= strength_req) &
        (df["Density"] <= density_req) &
        (df["Temperature"] >= temp_req)
    ].copy()

    if filtered.empty:
        filtered = df.copy()

    filtered["Score"] = (
        (filtered["Strength"] / strength_req) * 0.5 +
        (density_req / filtered["Density"]) * 0.3 +
        (filtered["Temperature"] / temp_req) * 0.2
    )

    return filtered.sort_values(by="Score", ascending=False)


@app.route("/", methods=["GET", "POST"])
def index():

    results = None

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

            chart_data = {
                "labels": list(results["Material"]),
                "strength": list(results["Strength"]),
                "density": list(results["Density"]),
                "temperature": list(results["Temperature"])
            }

        except Exception as e:
            print("ERROR:", e)

    return render_template("index.html", tables=results, chart_data=chart_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))