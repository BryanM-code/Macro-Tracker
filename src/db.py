import sqlite3


DEFAULT_GOALS = {
    "calorie_goal": 2200,
    "protein_goal": 180,
    "carb_goal": 220,
    "fat_goal": 70,
}


def get_connection(db_path):
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(db_path):
    with get_connection(db_path) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                calorie_goal REAL NOT NULL,
                protein_goal REAL NOT NULL,
                carb_goal REAL NOT NULL,
                fat_goal REAL NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                meal_type TEXT NOT NULL,
                description TEXT NOT NULL,
                calories REAL NOT NULL,
                protein REAL NOT NULL,
                carbs REAL NOT NULL,
                fat REAL NOT NULL
            )
            """
        )

        existing_goals = cursor.execute("SELECT id FROM goals LIMIT 1").fetchone()
        if not existing_goals:
            cursor.execute(
                """
                INSERT INTO goals (calorie_goal, protein_goal, carb_goal, fat_goal)
                VALUES (:calorie_goal, :protein_goal, :carb_goal, :fat_goal)
                """,
                DEFAULT_GOALS,
            )
        connection.commit()


def get_goal_settings(db_path):
    with get_connection(db_path) as connection:
        row = connection.execute("SELECT * FROM goals ORDER BY id LIMIT 1").fetchone()
        return dict(row)


def update_goal_settings(db_path, goals):
    cleaned = {
        "calorie_goal": _to_number(goals.get("calorie_goal")),
        "protein_goal": _to_number(goals.get("protein_goal")),
        "carb_goal": _to_number(goals.get("carb_goal")),
        "fat_goal": _to_number(goals.get("fat_goal")),
    }
    with get_connection(db_path) as connection:
        connection.execute(
            """
            UPDATE goals
            SET calorie_goal = :calorie_goal,
                protein_goal = :protein_goal,
                carb_goal = :carb_goal,
                fat_goal = :fat_goal
            WHERE id = (SELECT id FROM goals ORDER BY id LIMIT 1)
            """,
            cleaned,
        )
        connection.commit()


def save_meal(db_path, meal):
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO meals (date, meal_type, description, calories, protein, carbs, fat)
            VALUES (:date, :meal_type, :description, :calories, :protein, :carbs, :fat)
            """,
            meal,
        )
        connection.commit()
        return cursor.lastrowid


def get_daily_totals(db_path, selected_date):
    with get_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT
                COALESCE(SUM(calories), 0) AS calories,
                COALESCE(SUM(protein), 0) AS protein,
                COALESCE(SUM(carbs), 0) AS carbs,
                COALESCE(SUM(fat), 0) AS fat
            FROM meals
            WHERE date = ?
            """,
            (selected_date,),
        ).fetchone()
        return dict(row)


def get_history_for_date(db_path, selected_date):
    with get_connection(db_path) as connection:
        meals = connection.execute(
            """
            SELECT *
            FROM meals
            WHERE date = ?
            ORDER BY id DESC
            """,
            (selected_date,),
        ).fetchall()
    return [dict(meal) for meal in meals], get_daily_totals(db_path, selected_date)


def get_meal_dates(db_path):
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT DISTINCT date
            FROM meals
            ORDER BY date DESC
            """
        ).fetchall()
        return [row["date"] for row in rows]


def _to_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
