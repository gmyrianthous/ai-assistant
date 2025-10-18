from typing import Any


async def get_recipe(dish_name: str) -> dict[str, Any]:
    """
    Get a recipe for a specific dish.

    Args:
        dish_name: The name of the dish to get a recipe for

    Returns:
        A dictionary containing recipe information including ingredients and instructions
    """
    # Mock data - replace with real recipe API integration
    recipes = {
        'pasta carbonara': {
            'dish': 'Pasta Carbonara',
            'ingredients': [
                '400g spaghetti',
                '200g pancetta or guanciale',
                '4 large eggs',
                '100g Pecorino Romano cheese',
                'Black pepper',
                'Salt',
            ],
            'instructions': [
                'Cook pasta in salted boiling water until al dente',
                'Fry pancetta until crispy',
                'Mix eggs and grated cheese in a bowl',
                'Drain pasta, reserving pasta water',
                'Mix hot pasta with pancetta, then add egg mixture off heat',
                'Add pasta water to reach desired consistency',
                'Season with black pepper',
            ],
            'prep_time': '10 minutes',
            'cook_time': '15 minutes',
            'servings': 4,
            'note': 'Mock data - implement real recipe API',
        },
        'chocolate chip cookies': {
            'dish': 'Chocolate Chip Cookies',
            'ingredients': [
                '2 1/4 cups all-purpose flour',
                '1 tsp baking soda',
                '1 tsp salt',
                '1 cup butter, softened',
                '3/4 cup sugar',
                '3/4 cup brown sugar',
                '2 eggs',
                '2 tsp vanilla extract',
                '2 cups chocolate chips',
            ],
            'instructions': [
                'Preheat oven to 375°F (190°C)',
                'Mix flour, baking soda, and salt',
                'Cream butter and sugars',
                'Beat in eggs and vanilla',
                'Gradually blend in flour mixture',
                'Stir in chocolate chips',
                'Drop spoonfuls onto baking sheet',
                'Bake 9-11 minutes',
            ],
            'prep_time': '15 minutes',
            'cook_time': '10 minutes',
            'servings': 48,
            'note': 'Mock data - implement real recipe API',
        },
    }

    # Find matching recipe (case-insensitive)
    dish_lower = dish_name.lower()
    recipe = recipes.get(dish_lower)

    if recipe:
        return recipe

    # Return a generic response for unknown dishes
    return {
        'dish': dish_name,
        'error': f'Recipe for "{dish_name}" not found',
        'note': 'Mock data - implement real recipe API',
        'suggestions': list(recipes.keys()),
    }
