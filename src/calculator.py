def calculate_meal_totals(parsed_items):
    totals = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}

    for item in parsed_items:
        totals["calories"] += item["calories"]
        totals["protein"] += item["protein"]
        totals["carbs"] += item["carbs"]
        totals["fat"] += item["fat"]

    return {key: round(value, 1) for key, value in totals.items()}
