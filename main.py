from flask import Flask, request
import requests

app = Flask(__name__)

API_KEY = 'b605dccda5c140a2af82bba4c91815d9'
SPOONACULAR = 'https://api.spoonacular.com/recipes/findByIngredients'

# global variables
fulfillment_text = ''
recommended_food_ingredients = {}


def get_food_list(ingredients, number_fetched_food):
    spoonacular_api = SPOONACULAR
    ingredient_list = ''
    for ingredient in ingredients:
        ingredient_list += ingredient + ','
    parameters = {'ingredients': ingredient_list, 'number': number_fetched_food, 'apiKey': API_KEY}
    return requests.get(url=spoonacular_api, params=parameters)


def food_option_message(food_list, cordial=''):
    message = ''
    for i, food in enumerate(food_list):
        missing_ingredient_name = [ingredient.get('name') for ingredient in food_list[i].get('missedIngredients')]
        food_name = food_list[i].get('title')
        to_be = 'is' if len(missing_ingredient_name) < 2 else 'are'
        ingredient_s = 'ingredient' if len(missing_ingredient_name) < 2 else 'ingredients'
        missed_ingredients_message = 'You have to buy {0} more {1}, which {2}: {3}.'.format(
            len(missing_ingredient_name), ingredient_s, to_be, ', '.join(missing_ingredient_name))
        message += message_builder('', '', i + 1 if cordial == '' else cordial, food_name, missing_ingredient_name,
                                   missed_ingredients_message)
    return message


def message_builder(prepend, append, option_number, food, ingredients_list, ingredients_message):
    final_message = ' Option {0} : {1}. {2}'.format(option_number, food,
                                                    ingredients_message if len(ingredients_list) > 0 else '')
    return prepend + final_message + append


@app.route('/')
def index():
    return "This is Hossein Miraftabi's 3rd year project under the supervision of Riza"


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(force=True, silent=True)
    intent_name = req.get('queryResult').get('intent').get('displayName')
    if intent_name == 'food.ingredients':
        global fulfillment_text, recommended_food_ingredients
        ingredients = req.get('queryResult').get('parameters').get('ingredients')
        num_of_food = req.get('queryResult').get('parameters').get('number')
        num_of_food = 3 if num_of_food == '' else int(num_of_food)
        recommended_food_ingredients = get_food_list(ingredients, num_of_food).json()
        fulfillment_text = 'I found {0} options for you.{1}'.format(num_of_food,
                                                                    food_option_message(recommended_food_ingredients))
        return {
            "fulfillmentMessages": [{
                "text": {
                    "text": [fulfillment_text]
                }
            }]
        }
    elif intent_name == 'food.ingredients.repeatOptions':
        return {
            "fulfillmentMessages": [{
                "text": {
                    "text": ['Sure! ' + fulfillment_text]
                }
            }]
        }
    elif intent_name == 'food.ingredients.repeatOption':
        number = int(req.get('queryResult').get('parameters').get('ordinal'))
        fulfillment_text = food_option_message([recommended_food_ingredients[number - 1]], number)
        return {
            "fulfillmentMessages": [{
                "text": {
                    "text": [fulfillment_text]
                }
            }]
        }


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
