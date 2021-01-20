# from main import app, get_food_list
import main
import json


main.app.testing = True
client = main.app.test_client()


def payload(intent, number='', ordinal=''):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }
    data = {
        "queryResult": {
            "parameters": {
                "ingredients": ["cheese", "celery"],
                "number": number,
                "ordinal": ordinal
            },
            "intent": {
                "displayName": intent
            }
        }
    }
    url = '/webhook'
    return client.post(url, data=json.dumps(data), headers=headers)


def test_index_page_message():
    response = client.get("/")
    assert b"This is Hossein Miraftabi's 3rd year project under the supervision of Riza" == response.data


def test_webhook_content_type_is_json():
    response = payload('food.ingredients')
    assert response.content_type == 'application/json'


def test_list_food_contains_object_with_3_keys():
    payload('food.ingredients')
    first_object = main.list_of_food[0]
    assert len(first_object) == 3


def test_list_food_contains_object_with_id_as_number():
    payload('food.ingredients')
    first_object = main.list_of_food[0]
    food_id = first_object.get('id')
    assert type(food_id) is int


# def test_webhook_default_response():
#     response = payload('food.ingredients')
#     response_data = json.loads(response.data)
#     answer = 'I found 3 options for you. Option 1 : Celery Cheese Boats. You have to buy 1 more ingredient, ' \
#              'which is: carrot. Option 2 : Ants on a Log. You have to buy 1 more ingredient, which is: raisins.' \
#              ' Option 3 : Scrumptious Stuffed Celery. You have to buy 1 more ingredient, which is: fig spread.'
#     assert response_data["fulfillmentMessages"][0]["text"]["text"][0] == answer
    
    
# def test_webhook_2foods_response():
#     response = payload('food.ingredients', 2)
#     response_data = json.loads(response.data)
#     answer = 'I found 2 options for you. Option 1 : Ants on a Log. You have to buy 1 more ingredient, ' \
#              'which is: raisins. Option 2 : Scrumptious Stuffed Celery. You have to buy 1 more ingredient,' \
#              ' which is: fig spread.'
#     assert response_data["fulfillmentMessages"][0]["text"]["text"][0] == answer


def test_get_food_list_returns_200():
    assert main.get_food_list(["cheese", "celery"], 3).status_code == 200


def test_webhook_repeats_all_foods():
    payload('food.ingredients')
    response = payload('food.ingredients.repeatOptions')
    response_data = json.loads(response.data)
    answer = 'Sure! I found 3 options for you. Option 1 : Celery Cheese Boats. You have to buy 1 more ingredient, ' \
             'which is: carrot. Option 2 : Ants on a Log. You have to buy 1 more ingredient, which is: raisins.' \
             ' Option 3 : Scrumptious Stuffed Celery. You have to buy 1 more ingredient, which is: fig spread.'
    assert response_data["fulfillmentMessages"][0]["text"]["text"][0] == answer


def test_webhook_repeat_food():
    response = payload('food.ingredients.repeatOption', 2, 2)
    response_data = json.loads(response.data)
    answer = ' Option 2 : Ants on a Log. You have to buy 1 more ingredient, which is: raisins.'
    assert response_data["fulfillmentMessages"][0]["text"]["text"][0] == answer


def test_say_recipe_steps_exceed_upper_limit():
    instructions = ['Turn on oven', 'leave egg in the oven for 20 minutes']
    instruction = main.say_recipe_steps(instructions, 3)
    assert instruction == 'leave egg in the oven for 20 minutes'


def test_say_recipe_steps_exceed_lower_limit():
    instructions = ['Turn on oven', 'leave egg in the oven for 20 minutes']
    instruction = main.say_recipe_steps(instructions, 0)
    assert instruction == 'Turn on oven'


def test_intent_food_option():
    response = payload('food.option', 2)
    response_data = json.loads(response.data)
    assert type(response_data["fulfillmentMessages"][0]["text"]["text"][0]) == str



