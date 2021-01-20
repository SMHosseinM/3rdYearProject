from flask import Flask, request
import flask
import requests
from google.oauth2 import service_account
import googleapiclient.discovery


API_KEY = '7ee19186c3ea447a88bd977bcfea0d11'
SPOONACULAR = 'https://api.spoonacular.com/recipes/findByIngredients'
SCOPES = ['https://www.googleapis.com/auth/dialogflow']
SERVICE_ACCOUNT_FILE = './service.json'


app = Flask(__name__)
app.secret_key = 'SqKOIpeVaWcPYIfkPht6kmM_'

# global variables
fulfillment_text = ''
recommended_food_ingredients = {}
list_of_food = []
recipe_of_food = []
list_of_steps = []
recipe_instruction_step = 1


def get_food_list(ingredients, number_fetched_food):
    global list_of_food

    spoonacular_api = SPOONACULAR
    ingredient_list = ''
    for ingredient in ingredients:
        ingredient_list += ingredient + ','
    # parameters = {'ingredients': ingredient_list, 'number': number_fetched_food, 'apiKey': API_KEY}
    parameters = {'ingredients': ingredient_list, 'number': 25, 'apiKey': API_KEY}
    fetched_foods = requests.get(url=spoonacular_api, params=parameters).json()

    for fetched_food in fetched_foods:
        if fetched_food.get('likes') > 0:
            list_of_food.append(fetched_food)

        if len(list_of_food) == number_fetched_food:
            break


    # return requests.get(url=spoonacular_api, params=parameters)


def food_option_message(food_list, cordial=''):
    global list_of_food
    message = ''
    for i, food in enumerate(food_list):
        missing_ingredient_name = [ingredient.get('name') for ingredient in food.get('missedIngredients')]
        food_name = food.get('title')
        food_id = food.get('id')
        entity = {
            'id': food_id,
            'value': food_name,
            'synonyms': []
        }
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


def get_food_info(food_number):
    global list_of_food, recipe_of_food
    food_id = list_of_food[food_number-1].get('id')
    spoonacular_food_info = 'https://api.spoonacular.com/recipes/' + str(food_id) + '/analyzedInstructions'
    parameter = {'apiKey': API_KEY}
    result = requests.get(url=spoonacular_food_info, params=parameter)
    recipe_of_food.append(result.json())


def say_recipe_steps(instructions, step_number):
    global recipe_instruction_step
    print('step number: ', step_number)
    if step_number > len(instructions):
        step_index = len(instructions)-1
        recipe_instruction_step = step_index
    elif step_number < 1:
        step_index = 1
        recipe_instruction_step = step_index
    else:
        recipe_instruction_step = step_number
    return instructions[recipe_instruction_step-1].get('step')



@app.route('/')
def index():
    return "This is Hossein Miraftabi's 3rd year project under the supervision of Riza"


@app.route('/webhook', methods=['POST'])
def webhook():
    global recipe_instruction_step, list_of_steps
    req = request.get_json(force=True, silent=True)
    intent_name = req.get('queryResult').get('intent').get('displayName')
    print(intent_name)
    if intent_name == 'food.ingredients':
        recipe_instruction_step = 1
        global list_of_food
        list_of_food = []
        global fulfillment_text, recommended_food_ingredients
        ingredients = req.get('queryResult').get('parameters').get('ingredients')
        num_of_food = req.get('queryResult').get('parameters').get('number')
        num_of_food = 3 if num_of_food == '' else int(num_of_food)
        get_food_list(ingredients, num_of_food)
        fulfillment_text = 'I found {0} options for you.{1}'.format(num_of_food,
                                                                    food_option_message(list_of_food))

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
    elif intent_name == 'food.option':
        global list_of_steps
        option_number = -1
        option_ordinal = -1
        try:
            option_ordinal = int(req.get('queryResult').get('parameters').get('ordinal'))
        except:
            option_number = req.get('queryResult').get('parameters').get('number')
        food_index = option_number if option_number != -1 else option_ordinal
        get_food_info(food_index)
        selected_food_steps = recipe_of_food[0][0].get('steps')
        for obj in selected_food_steps:
            list_of_steps.append(obj.get('step'))
        list_of_steps = [step for step in selected_food_steps]
        print(recipe_instruction_step)
        instruction = say_recipe_steps(list_of_steps, recipe_instruction_step)
        return {
            "fulfillmentMessages": [{
                "text": {
                    "text": [instruction]
                }
            }]
        }
    elif intent_name == 'recipe.next':
        print('here')
        instruction = say_recipe_steps(list_of_steps, recipe_instruction_step+1)
        return {
            "fulfillmentMessages": [{
                "text": {
                    "text": [instruction]
                }
            }]
        }
    elif intent_name == 'recipe.previous':
        instruction = say_recipe_steps(list_of_steps, recipe_instruction_step-1)
        return {
            "fulfillmentMessages": [{
                "text": {
                    "text": [instruction]
                }
            }]
        }


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
