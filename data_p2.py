"""Mock data for the Recipe Nutrition Agent.

All keys are lowercase. Normalise inputs with .strip().lower() before lookups.

Design notes
------------
- RECIPES stores grams for ONE serving; find_recipe scales by `servings`.
- NUTRITION stores kcal per 100 g; get_nutrition computes kcal for the given grams.
- DIETARY stores, per ingredient, the flags that ingredient is compatible with.
  A dish gets a flag only if EVERY ingredient has it. An ingredient missing from
  DIETARY can't be confirmed, so it blocks every flag (the conservative choice).
- Deliberate gaps for testing:
    * "truffle mushroom pasta" uses "truffle oil", which is in no table, so
      get_nutrition should return an error string -> agent sets confidence='low'.
    * "moon soup" is in no table at all -> find_recipe should return an error string.
"""

# grams per ONE serving
RECIPES: dict[str, dict[str, float]] = {
    "mushroom risotto": {
        "arborio rice": 80.0,
        "mushrooms": 150.0,
        "onion": 50.0,
        "vegetable stock": 250.0,
        "parmesan": 20.0,
        "butter": 10.0,
        "olive oil": 10.0,
    },
    "spaghetti carbonara": {
        "spaghetti": 100.0,
        "eggs": 60.0,
        "pancetta": 50.0,
        "pecorino": 20.0,
        "black pepper": 1.0,
    },
    "chickpea curry": {
        "chickpeas": 150.0,
        "chopped tomatoes": 200.0,
        "onion": 50.0,
        "coconut milk": 100.0,
        "curry powder": 5.0,
        "olive oil": 10.0,
    },
    "truffle mushroom pasta": {
        "spaghetti": 100.0,
        "mushrooms": 120.0,
        "truffle oil": 5.0,      # intentionally missing from NUTRITION and DIETARY
        "parmesan": 15.0,
    },
}

# kcal per 100 g (approximate real-world values)
NUTRITION: dict[str, float] = {
    "arborio rice": 350.0,
    "mushrooms": 22.0,
    "onion": 40.0,
    "vegetable stock": 5.0,
    "parmesan": 431.0,
    "butter": 717.0,
    "olive oil": 884.0,
    "spaghetti": 371.0,
    "eggs": 143.0,
    "pancetta": 458.0,
    "pecorino": 387.0,
    "black pepper": 251.0,
    "chickpeas": 139.0,
    "chopped tomatoes": 21.0,
    "coconut milk": 197.0,
    "curry powder": 325.0,
}

# flags each ingredient is compatible with
DIETARY: dict[str, set[str]] = {
    "arborio rice":     {"vegetarian", "vegan", "gluten_free", "dairy_free"},
    "mushrooms":        {"vegetarian", "vegan", "gluten_free", "dairy_free"},
    "onion":            {"vegetarian", "vegan", "gluten_free", "dairy_free"},
    "vegetable stock":  {"vegetarian", "vegan", "gluten_free", "dairy_free"},
    "parmesan":         {"gluten_free"},  # traditional parmesan uses animal rennet
    "butter":           {"vegetarian", "gluten_free"},
    "olive oil":        {"vegetarian", "vegan", "gluten_free", "dairy_free"},
    "spaghetti":        {"vegetarian", "vegan", "dairy_free"},
    "eggs":             {"vegetarian", "gluten_free", "dairy_free"},
    "pancetta":         {"gluten_free", "dairy_free"},
    "pecorino":         {"gluten_free"},
    "black pepper":     {"vegetarian", "vegan", "gluten_free", "dairy_free"},
    "chickpeas":        {"vegetarian", "vegan", "gluten_free", "dairy_free"},
    "chopped tomatoes": {"vegetarian", "vegan", "gluten_free", "dairy_free"},
    "coconut milk":     {"vegetarian", "vegan", "gluten_free", "dairy_free"},
    "curry powder":     {"vegetarian", "vegan", "gluten_free", "dairy_free"},
}

ALL_FLAGS = ("vegetarian", "vegan", "gluten_free", "dairy_free")

# Expected values for one serving, handy for pytest:
#   mushroom risotto      -> 280 + 33 + 20 + 12.5 + 86.2 + 71.7 + 88.4 = 591.8 kcal
#                            flags: ['gluten_free']   (parmesan blocks vegetarian)
#   chickpea curry        -> 208.5 + 42 + 20 + 197 + 16.25 + 88.4 = 572.15 kcal
#                            flags: all four
#   spaghetti carbonara   -> flags: []  (pancetta, pecorino and wheat spaghetti)
#   truffle mushroom pasta-> 'truffle oil' missing -> error string, confidence='low'