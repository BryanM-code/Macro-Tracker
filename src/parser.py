import json
import re


NUMBER_WORDS = {
    "a": 1,
    "an": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}

CONNECTOR_PATTERN = re.compile(r"\s*(?:,|\band\b|\bwith\b|\+)\s*", re.IGNORECASE)
QUANTITY_PATTERN = re.compile(r"(?P<quantity>\d+(?:\.\d+)?)|(?P<word>a|an|one|two|three|four|five)\b", re.IGNORECASE)


def load_foods(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def parse_meal_description(description, foods_catalog):
    if not description.strip():
        return []

    parts = [part.strip() for part in CONNECTOR_PATTERN.split(description) if part.strip()]
    parsed_items = []

    for part in parts:
        parsed_items.append(_parse_single_item(part, foods_catalog))

    return parsed_items


def _parse_single_item(raw_text, foods_catalog):
    normalized_text = raw_text.lower().strip()
    quantity = _extract_quantity(normalized_text)
    matched_food = _find_best_food_match(normalized_text, foods_catalog)

    if matched_food:
        item_totals = {
            "calories": round(matched_food["calories"] * quantity, 1),
            "protein": round(matched_food["protein"] * quantity, 1),
            "carbs": round(matched_food["carbs"] * quantity, 1),
            "fat": round(matched_food["fat"] * quantity, 1),
        }
        return {
            "raw_text": raw_text,
            "quantity": quantity,
            "matched": True,
            "food_name": matched_food["name"],
            "serving_unit": matched_food["serving_unit"],
            "calories": item_totals["calories"],
            "protein": item_totals["protein"],
            "carbs": item_totals["carbs"],
            "fat": item_totals["fat"],
        }

    return {
        "raw_text": raw_text,
        "quantity": quantity,
        "matched": False,
        "food_name": "Unrecognized item",
        "serving_unit": "",
        "calories": 0.0,
        "protein": 0.0,
        "carbs": 0.0,
        "fat": 0.0,
    }


def _extract_quantity(text):
    match = QUANTITY_PATTERN.search(text)
    if not match:
        return 1.0

    numeric_quantity = match.group("quantity")
    if numeric_quantity:
        try:
            return float(numeric_quantity)
        except ValueError:
            return 1.0

    word_quantity = match.group("word")
    return float(NUMBER_WORDS.get(word_quantity.lower(), 1))


def _find_best_food_match(text, foods_catalog):
    best_match = None
    best_score = 0

    for food in foods_catalog:
        aliases = food.get("aliases", []) + [food["name"]]
        for alias in aliases:
            alias_text = alias.lower()
            if alias_text in text:
                score = len(alias_text)
                if score > best_score:
                    best_match = food
                    best_score = score

    return best_match
