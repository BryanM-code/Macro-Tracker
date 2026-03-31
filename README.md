# Macro Tracker

Macro Tracker is a simple web app mainly made from my own personal meals as references for data. This will help me and soon other users to track their macros

## Features

- Add a meal using plain text Ex: `2 eggs, 2 slices wheat bread, 1 banana`
- Split text into basic food matches from a built-in food dataset (json files)
- Estimate calories, protein, carbs, and fat
- Save meals locally in SQLite for future references 
- View today's totals and remaining macros on the dashboard Ex: `You currently need 300 more calories to fullfil today's goal`
- Update daily nutrition goals as user desires
- Review meal history by date

## Tech Stack

- Python
- Flask
- SQLite
- HTML, CSS, JavaScript

## How to run app locally

Open `http://127.0.0.1:5000` in your browser.

## How It Works

- Foods are stored in [`foods.json`] (currently limited data, only accommodates for my personal meals).
- The parser uses text splitting and alias matching to identify likely food items and rough quantities.
- Macro totals are calculated from the matched foods.
- Meals and goals are stored in SQLite.

## Tools used

- AI tools (Claude) were used to assist with frontend design as well as logic in parser for text splitting and alias matching.

## Notes

- If a food is not recognized, the app keeps the raw item text so the user can still see what was attempted. It will not getting added to sum.

