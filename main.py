from flask import Flask, request
from nltk import ngrams
from nltk.tokenize import word_tokenize
import requests
import transformerCode
import recipeContentNavigation
import foodNameSearch
# from transformers import pipeline


API_KEY = '7ee19186c3ea447a88bd977bcfea0d11'
SPOONACULAR = 'https://api.spoonacular.com/recipes/findByIngredients'
SCOPES = ['https://www.googleapis.com/auth/dialogflow']
SERVICE_ACCOUNT_FILE = './service.json'


app = Flask(__name__)
app.secret_key = 'SqKOIpeVaWcPYIfkPht6kmM_'

# global variables
fulfillment_text = ''
list_of_food = []
list_of_food_titles = []
recipe_of_food = []
list_of_steps = []
recipe_instruction_step = 1
current_instruction = ''
is_current_recipe_navigation = False
question_query_text = ""
selected_food_to_repeat = []
recommended_food_options = ''


def get_food_list(ingredients, number_fetched_food):
    global list_of_food, list_of_food_titles
    list_of_food_titles = []

    spoonacular_api = SPOONACULAR
    ingredient_list = ''
    for ingredient in ingredients:
        ingredient_list += ingredient + ','
    # parameters = {'ingredients': ingredient_list, 'number': number_fetched_food, 'apiKey': API_KEY}
    parameters = {'ingredients': ingredient_list, 'number': 25, 'apiKey': API_KEY}
    fetched_foods = requests.get(url=spoonacular_api, params=parameters).json()

    for fetched_food in fetched_foods:
        if fetched_food.get('likes') > 1:
            list_of_food.append(fetched_food)
            list_of_food_titles.append(fetched_food['title'])

        if len(list_of_food) == number_fetched_food:
            break


    # return requests.get(url=spoonacular_api, params=parameters)


def food_option_message(food_list, cordial=''):
    global list_of_food
    message = ''
    for i, food in enumerate(food_list):
        missing_ingredient_name = [ingredient.get('name') for ingredient in food.get('missedIngredients')]
        food_name = food.get('title').lower()
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
    recipe_of_food = []
    recipe_of_food.append(result.json())


def say_recipe_steps(instructions, step_number):
    global recipe_instruction_step
    print('step number: ', step_number)
    if step_number > len(instructions):
        step_index = len(instructions)+1
        recipe_instruction_step = step_index
        return '''You have reached the end of the instructions. You have three options to choose from:
        You can navigate to the previous instruction by saying "previous",
        you can end the conversation by saying "I'm done", 
        or you can start a new conversation by listing your ingredients!'''
    elif step_number < 1:
        step_index = 0
        recipe_instruction_step = step_index
        return 'Please type "next" to see the first instruction'
    else:
        recipe_instruction_step = step_number
    return instructions[recipe_instruction_step-1].get('step')


def get_recipe_equipments(recipe_id):
    spoonacular_food_equipments = 'https://api.spoonacular.com/recipes/' + str(recipe_id) + '/equipmentWidget.json'
    parameter = {'apiKey': API_KEY}
    result = requests.get(url=spoonacular_food_equipments, params=parameter)
    return result.json()


@app.route('/')
def index():
    return "This is Hossein Miraftabi's 3rd year project under the supervision of Riza Batista"


@app.route('/webhook', methods=['POST'])
def webhook():
    global recipe_instruction_step, list_of_steps, current_instruction, is_current_recipe_navigation, \
        question_query_text, selected_food_to_repeat, fulfillment_text, recommended_food_options
    req = request.get_json(force=True, silent=True)
    intent_name = req.get('queryResult').get('intent').get('displayName')
    print(intent_name)

    # check if the intent is recipe content or not
    if is_current_recipe_navigation and intent_name != 'recipe.next' and intent_name != 'recipe.previous' \
            and intent_name != 'food.option' and intent_name != 'food.ingredients.repeatOption' \
            and intent_name != 'food.ingredients.repeatOptions':
        query_text = req.get('queryResult').get('queryText')
        if query_text != 'select-food-by-name-event' and query_text != 'recipe-content-event':
            print('query text is:', query_text)
            predict_text = recipeContentNavigation.svm.predict(recipeContentNavigation.count_vect.transform([query_text]))
            print('prediction is: ', predict_text)
            if intent_name == 'food.ingredients' and predict_text == 'food-name':
                predict_text = 'none'
            if predict_text == 'recipe-content':
                if intent_name != 'option.recipe.question':
                    intent_dic = req.get('queryResult').get('intent')
                    print('intent_dic is: ', intent_dic)
                    intent_dic['displayName'] = 'option.recipe.question'
                    print('intent_dic is: ', intent_dic)
                    print('query_text is : ', query_text)
                    question_query_text = query_text
                    return {
                        "followupEventInput": {
                            "name": "recipe-content-event",
                            "languageCode": "en-US"
                        }
                    }
            elif predict_text == 'food-name':
                result = foodNameSearch.food_name_search(list_of_food_titles, query_text)
                if result > -1:
                    return {
                        "followupEventInput": {
                            "name": "select-food-by-name-event",
                            "parameters": {
                                "number": result,
                                "ordinal": ""
                            },
                            "languageCode": "en-US"
                        }
                    }
                else:
                    message = '''I'm sorry but the name of the food option is not recognised!
                    To see the list of recommended food options, please say 'show me the list of recommended food options'''''
                    return {
                        "fulfillmentMessages": [{
                            "text": {
                                "text": [message]
                            }
                        }],

                        "payload": {
                            "google": {
                                "expectUserResponse": True,
                                "richResponse": {
                                    "items": [
                                        {
                                            "simpleResponse": {
                                                "textToSpeech": message
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    }
    # end of checking process

    if intent_name == 'food.ingredients':
        is_current_recipe_navigation = True
        recipe_instruction_step = 1
        global list_of_food
        list_of_food = []
        # global fulfillment_text
        ingredients = req.get('queryResult').get('parameters').get('ingredients')
        if len(ingredients) == 0:
            return {
                "fulfillmentMessages": [{
                    "text": {
                        "text": ['Please tell me what ingredients you have.']
                    }
                }],

                "payload": {
                    "google": {
                        "expectUserResponse": True,
                        "richResponse": {
                            "items": [
                                {
                                    "simpleResponse": {
                                        "textToSpeech": 'Please tell me what ingredients you have.'
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        print('ingredients are:', ingredients)
        num_of_food = req.get('queryResult').get('parameters').get('number')
        num_of_food = 3 if num_of_food == '' else int(num_of_food)
        get_food_list(ingredients, num_of_food)
        fulfillment_text = 'I found {0} options for you.{1}'.format(num_of_food,
                                                                    food_option_message(list_of_food))
        fulfillment_text += 'Please select your favourite food option by calling its name or its option number.'
        recommended_food_options = fulfillment_text

        return {
            "fulfillmentMessages": [{
                "text": {
                    "text": [fulfillment_text]
                }
            }],

            "payload": {
                "google": {
                    "expectUserResponse": True,
                    "richResponse": {
                        "items": [
                            {
                                "simpleResponse": {
                                    "textToSpeech": fulfillment_text
                                }
                            }
                        ]
                    }
                }
            }
        }
    elif intent_name == 'repeat.recommended.food.list':
        return {
            "fulfillmentMessages": [{
                "text": {
                    "text": [recommended_food_options]
                }
            }],

            "payload": {
                "google": {
                    "expectUserResponse": True,
                    "richResponse": {
                        "items": [
                            {
                                "simpleResponse": {
                                    "textToSpeech": recommended_food_options
                                }
                            }
                        ]
                    }
                }
            }
        }
    elif intent_name == 'food.ingredients.repeatOptions':
        is_current_recipe_navigation = True
        return {
            "fulfillmentMessages": [{
                "text": {
                    "text": ['Sure! ' + fulfillment_text]
                }
            }],

            "payload": {
                "google": {
                    "expectUserResponse": True,
                    "richResponse": {
                        "items": [
                            {
                                "simpleResponse": {
                                    "textToSpeech": 'Sure! ' + fulfillment_text
                                }
                            }
                        ]
                    }
                }
            }
        }
    elif intent_name == 'food.ingredients.repeatOption':
        is_current_recipe_navigation = True
        try:
            number = int(req.get('queryResult').get('parameters').get('ordinal'))
        except:
            number = int(req.get('queryResult').get('parameters').get('number'))
        fulfillment_text = food_option_message([list_of_food[number - 1]], number)
        selected_food_to_repeat.append(fulfillment_text)
        print(selected_food_to_repeat[0])
        return {
            "fulfillmentMessages": [{
                "text": {
                    "text": [fulfillment_text]
                }
            }],

            "payload": {
                "google": {
                    "expectUserResponse": True,
                    "richResponse": {
                        "items": [
                            {
                                "simpleResponse": {
                                    "textToSpeech": fulfillment_text
                                }
                            }
                        ]
                    }
                }
            }
        }
    elif intent_name == 'food.option':
        is_current_recipe_navigation = True
        global list_of_steps
        option_number = -1
        option_ordinal = -1
        try:
            option_ordinal = int(req.get('queryResult').get('parameters').get('ordinal'))
        except:
            option_number = req.get('queryResult').get('parameters').get('number')
        food_index = int(option_number) if option_number != -1 else option_ordinal
        get_food_info(food_index)
        try:
            selected_food_steps = recipe_of_food[0][0].get('steps')
        except IndexError:
            message = '''I'm affraid that the cooking instructions for this food option are not available! 
            To see the list of recommended food options, please say "show me the list of recommended food options"'''
            return {
                "fulfillmentMessages": [{
                    "text": {
                        "text": [message]
                    }
                }],

                "payload": {
                    "google": {
                        "expectUserResponse": True,
                        "richResponse": {
                            "items": [
                                {
                                    "simpleResponse": {
                                        "textToSpeech": message
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        for obj in selected_food_steps:
            list_of_steps.append(obj.get('step'))
        list_of_steps = [step for step in selected_food_steps]
        print('The step number is: ', recipe_instruction_step)
        instruction = ''' {}
        After any of the instructions, you can choose from a number of commands.
        To listen to the same instruction again, please say something like "repeat".
        To navigate to the next instruction, please say something like "next".
        To go back to the previous instruction, please say something like "previous".'''\
            .format(say_recipe_steps(list_of_steps, recipe_instruction_step))
        current_instruction = instruction
        return {
            "fulfillmentMessages": [{
                "text": {
                    "text": [instruction]
                }
            }],

            "payload": {
                "google": {
                    "expectUserResponse": True,
                    "richResponse": {
                        "items": [
                            {
                                "simpleResponse": {
                                    "textToSpeech": instruction
                                }
                            }
                        ]
                    }
                }
            }
        }
    elif intent_name == 'recipe.next':
        is_current_recipe_navigation = True
        print('here')
        instruction = say_recipe_steps(list_of_steps, recipe_instruction_step+1)
        current_instruction = instruction
        return {
            "fulfillmentMessages": [{
                "text": {
                    "text": [instruction]
                }
            }],

            "payload": {
                "google": {
                    "expectUserResponse": True,
                    "richResponse": {
                        "items": [
                            {
                                "simpleResponse": {
                                    "textToSpeech": instruction
                                }
                            }
                        ]
                    }
                }
            }
        }
    elif intent_name == 'recipe.previous':
        is_current_recipe_navigation = True
        instruction = say_recipe_steps(list_of_steps, recipe_instruction_step-1)
        current_instruction = instruction
        return {
            "fulfillmentMessages": [{
                "text": {
                    "text": [instruction]
                }
            }],

            "payload": {
                "google": {
                    "expectUserResponse": True,
                    "richResponse": {
                        "items": [
                            {
                                "simpleResponse": {
                                    "textToSpeech": instruction
                                }
                            }
                        ]
                    }
                }
            }
        }
    elif intent_name == 'recipe.fallback':
        message = '''Sorry! I didn't understand what you mean.
        To listen to the same instruction again, please say something like "repeat".
        To navigate to the next instruction, please say something like "next".
        To go back to the previous instruction, please say something like "previous"'''
        return {
            "fulfillmentMessages": [{
                "text": {
                    "text": [message]
                }
            }],

            "payload": {
                "google": {
                    "expectUserResponse": True,
                    "richResponse": {
                        "items": [
                            {
                                "simpleResponse": {
                                    "textToSpeech": message
                                }
                            }
                        ]
                    }
                }
            }
        }
        # return {
        #     "followupEventInput": {
        #         "name": "recipe-content-event",
        #         "languageCode": "en-US"
        #     }
        # }

    elif intent_name == 'recipe-content-queries':
        if question_query_text == "":
            question = req.get('queryResult').get('queryText')
        else:
            question = question_query_text
            question_query_text = ""
        context = current_instruction
        question_answerer = transformerCode.get_pipeline()
        answer = question_answerer(question=question, context=context)
        score = answer.get('score')
        if score < 0.2:
            message = "Sorry! I couldn't find the answer to your question."
        else:
            message = answer.get('answer')
        final_answer = '{}'.format(message)
        return {
            "fulfillmentMessages": [{
                "text": {
                    "text": [final_answer]
                }
            }],

            "payload": {
                "google": {
                    "expectUserResponse": True,
                    "richResponse": {
                        "items": [
                            {
                                "simpleResponse": {
                                    "textToSpeech": final_answer
                                }
                            }
                        ]
                    }
                }
            }
        }
    elif intent_name == 'food.option.recipe.repeat':
        instruction = say_recipe_steps(list_of_steps, recipe_instruction_step)
        message = '{}'.format(instruction)
        return {
            "fulfillmentMessages": [{
                "text": {
                    "text": [message]
                }
            }],

            "payload": {
                "google": {
                    "expectUserResponse": True,
                    "richResponse": {
                        "items": [
                            {
                                "simpleResponse": {
                                    "textToSpeech": message
                                }
                            }
                        ]
                    }
                }
            }
        }
    #elif intent_name == 'option.pronoun':
    #    option = selected_food_to_repeat[0]
    #    selected_food_to_repeat = []
    #    before_keyword, keyword, after_keyword = option.partition("Option")
    #    number = int(after_keyword.strip()[0])
    #    print(number)
    #    return {
    #        "followupEventInput": {
    #            "name": "select-food-by-name-event",
    #            "parameters": {
    #                "number": number,
    #                "ordinal": ""
    #            },
    #            "languageCode": "en-US"
    #        }
    #    }
    elif intent_name == 'food.ingredients.fallback':
        list_of_food_name = []
        list_of_food_dict = []
        for food in list_of_food:
            food_name = food.get('title').lower()
            food_tokenization = tuple(word_tokenize(food_name))
            list_of_food_name.append(food.get('title').lower())
            list_of_food_dict.append({food_tokenization: len(food_tokenization)})

        asked_food = req.get('queryResult').get('queryText').lower()
        print(asked_food)
        print(list_of_food_name)
        for i, food in enumerate(list_of_food_name):
            food_tokenization = tuple(word_tokenize(food))
            print(tuple(word_tokenize(food)))
            n = len(food_tokenization)
            ngram = ngrams(asked_food.split(), n)
            for grams in ngram:
                print(grams)
                if grams == food_tokenization:
                    return {
                        "followupEventInput": {
                            "name": "select-food-by-name-event",
                            "parameters": {
                                "number": i+1,
                                "ordinal": ""
                            },
                            "languageCode": "en-US"
                        }
                    }
        if len(list_of_food_titles) == 0:
            message = "I'm afraid I don't recognise these ingredients! Please name other ingredients."
        else:
            message = "name of the food is not recognize. To see the list of recommended food, " \
                      "please say 'show me the list of recommended food"
        return {
            "fulfillmentMessages": [{
                "text": {
                    "text": [message]
                }
            }],

            "payload": {
                "google": {
                    "expectUserResponse": True,
                    "richResponse": {
                        "items": [
                            {
                                "simpleResponse": {
                                    "textToSpeech": message
                                }
                            }
                        ]
                    }
                }
            }
        }


        # print(list_of_food_name)
        # print(list_of_food_dict)
        # return {
        #     "fulfillmentMessages": [{
        #         "text": {
        #             "text": ["This is the fallback for ingredients"]
        #         }
        #     }]
        # }
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
