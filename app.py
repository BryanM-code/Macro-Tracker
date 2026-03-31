from datetime import date
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

from src.calculator import calculate_meal_totals
from src.db import (
    get_daily_totals,
    get_goal_settings,
    get_history_for_date,
    get_meal_dates,
    init_db,
    save_meal,
    update_goal_settings,
)
from src.parser import load_foods, parse_meal_description


BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
app.config["DATABASE"] = BASE_DIR / "macro_tracker.db"

foods_catalog = load_foods(BASE_DIR / "foods.json")
init_db(app.config["DATABASE"])


@app.route("/")
def dashboard():
    today = date.today().isoformat()
    goals = get_goal_settings(app.config["DATABASE"])
    totals = get_daily_totals(app.config["DATABASE"], today)
    remaining = {
        "calories": goals["calorie_goal"] - totals["calories"],
        "protein": goals["protein_goal"] - totals["protein"],
        "carbs": goals["carb_goal"] - totals["carbs"],
        "fat": goals["fat_goal"] - totals["fat"],
    }
    return render_template(
        "dashboard.html",
        today=today,
        goals=goals,
        totals=totals,
        remaining=remaining,
    )


@app.route("/add-meal", methods=["GET", "POST"])
def add_meal():
    result = None
    if request.method == "POST":
        description = request.form.get("description", "").strip()
        meal_type = request.form.get("meal_type", "breakfast")

        parsed_items = parse_meal_description(description, foods_catalog)
        totals = calculate_meal_totals(parsed_items)

        meal_id = save_meal(
            app.config["DATABASE"],
            {
                "date": date.today().isoformat(),
                "meal_type": meal_type,
                "description": description,
                "calories": totals["calories"],
                "protein": totals["protein"],
                "carbs": totals["carbs"],
                "fat": totals["fat"],
            },
        )

        result = {
            "meal_id": meal_id,
            "description": description,
            "meal_type": meal_type,
            "items": parsed_items,
            "totals": totals,
        }

    return render_template("add_meal.html", result=result)


@app.route("/history")
def history():
    selected_date = request.args.get("date") or date.today().isoformat()
    available_dates = get_meal_dates(app.config["DATABASE"])
    meals, totals = get_history_for_date(app.config["DATABASE"], selected_date)
    return render_template(
        "history.html",
        selected_date=selected_date,
        available_dates=available_dates,
        meals=meals,
        totals=totals,
    )


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        update_goal_settings(
            app.config["DATABASE"],
            {
                "calorie_goal": request.form.get("calorie_goal", 0),
                "protein_goal": request.form.get("protein_goal", 0),
                "carb_goal": request.form.get("carb_goal", 0),
                "fat_goal": request.form.get("fat_goal", 0),
            },
        )
        return redirect(url_for("settings"))

    goals = get_goal_settings(app.config["DATABASE"])
    return render_template("settings.html", goals=goals)


if __name__ == "__main__":
    app.run(debug=True)
