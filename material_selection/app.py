from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# Load data
data = pd.read_csv("materials.csv")


# ✅ Improved Function (Filtering + Ranking)
def rank_materials(df, strength_req, density_req, temp_req):

    # 🔥 Step 1: Apply strict filtering
    filtered = df[
        (df["Strength"] >= strength_req) &
        (df["Density"] <= density_req) &
        (df["Temperature"] >= temp_req)
    ].copy()

    # 🔁 If no materials match → fallback to all data
    if filtered.empty:
        filtered = df.copy()

    # 🔥 Step 2: Normalize scores
    filtered["Strength_score"] = filtered["Strength"] / strength_req
    filtered["Density_score"] = density_req / filtered["Density"]
    filtered["Temp_score"] = filtered["Temperature"] / temp_req

    # 🔥 Step 3: Final score calculation
    filtered["Score"] = (
        filtered["Strength_score"] * 0.5 +
        filtered["Density_score"] * 0.3 +
        filtered["Temp_score"] * 0.2
    )

    return filtered.sort_values(by="Score", ascending=False)


@app.route("/", methods=["GET", "POST"])
def index():

    results = None
    chart_data = None

    if request.method == "POST":

        strength = float(request.form["strength"])
        density = float(request.form["density"])
        temperature = float(request.form["temperature"])

        ranked = rank_materials(data.copy(), strength, density, temperature)

        # ✅ Show top 5 best materials
        results = ranked.head(5)

        # ✅ Safe chart data (avoid error)
        chart_data = {
            "labels": list(results["Material"]),
            "strength": list(results["Strength"]),
            "density": list(results["Density"]),
            "temperature": list(results["Temperature"])
        }

    return render_template(
        "index.html",
        tables=results,
        chart_data=chart_data
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))