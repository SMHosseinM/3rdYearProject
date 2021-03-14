from transformers import pipeline

q_and_a = pipeline("question-answering", model='distilbert-base-cased-distilled-squad')


def get_pipeline():
    return q_and_a
