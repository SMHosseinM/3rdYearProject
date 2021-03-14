from nltk.tokenize import word_tokenize
from nltk import ngrams
import re
import nltk
nltk.download('punkt')


def food_name_search(food_name_list, context):
    sentence = context
    sentence = sentence.lower()
    sentence = re.sub(r'[^\w\s]', '', sentence)
    for i, name in enumerate(food_name_list):
        food_name = name.lower()
        food_name = re.sub(r'[^\w\s]', '', food_name)
        print('food name is', food_name)
        nltk_tokens = word_tokenize(food_name)
        print(nltk_tokens)

        some_grams = ngrams(sentence.split(), len(nltk_tokens))

        for grams in some_grams:
            print(grams)
            # if grams == grams_token_list[0]:
            if grams == tuple(nltk_tokens):
                print('BOOM!')
                return i+1
    return -1
