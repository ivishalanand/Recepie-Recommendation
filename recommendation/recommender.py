import pickle
import re

import nltk
import numpy as np
import pandas as pd
from nltk.corpus import stopwords

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
from gensim.models.keyedvectors import KeyedVectors
from sklearn.metrics.pairwise import cosine_similarity


def get_data():
    with open("/Users/visanand2/Desktop/Pycharm/Recepie-Recommendation/scraper/data.pkl", 'rb') as f:
        data = pickle.load(f)
        return data


def preprocess(data):
    meal = [data[i][1]["meal"] for i in range(len(data))]
    reviews = [data[i][1]["reviews"] for i in range(len(data))]
    description = [data[i][1]["description"] for i in range(len(data))]
    prep_time = [data[i][1]["prep_time"] for i in range(len(data))]
    region = [data[i][1]["region"] for i in range(len(data))]
    portion_size = [data[i][1]["portion_size"] for i in range(len(data))]
    basic_ingredients = [data[i][1]["basic_ingredients"] for i in range(len(data))]
    cooking_instruction = [data[i][1]["cooking_instruction"] for i in range(len(data))]
    nutritional_info = [data[i][1]["nutritional_info"] for i in range(len(data))]
    ingredients = [data[i][1]["ingredients"] for i in range(len(data))]
    allergen = [data[i][1]["allergen"] for i in range(len(data))]
    rating = [data[i][1]["rating"] for i in range(len(data))]

    df = pd.DataFrame({"meal": meal,
                       "reviews": reviews,
                       "description": description,
                       "prep_time": prep_time,
                       "region": region,
                       "basic_ingredients": basic_ingredients,
                       "cooking_instruction": cooking_instruction,
                       "ingredients": ingredients,
                       "allergen": allergen,
                       "rating": rating,
                       "nutritional_info": nutritional_info
                       })
    return df


def process_sentence(sentence):
    sentence = sentence.replace("†", '')
    sentence = sentence.lower()  # lower casing
    sentence = ' '.join([w for w in sentence.split() if not w in stop_words])  # removing stop words
    sentence = ' '.join(s for s in sentence.split() if
                        not any(c.isdigit() for c in s))  # removing digits contained word ( servings/ quantity)
    sentence = re.sub(r'\W+', ' ', sentence)  # remove alpha numeric char
    sentence = ' '.join(i for i in sentence.split() if i not in ["tsp", 'tbsp', 'with'])  # removing tbsp and tsp
    sentence = ' '.join(i for i in sentence.split() if len(i) > 1)  # removing singel length word
    sentence = sentence.strip()  # removing forward and last space
    return sentence


def text_processing(sentences, column):
    processed = []

    if column == "ingredients":
        for sentence in sentences:
            sentence = process_sentence(sentence)
            processed.append(sentence)

    elif column == "meal":
        processed = process_sentence(sentences)

    return processed


def merge_context(processed_ingredients, processed_meal):
    merged = processed_ingredients
    merged.extend(processed_meal.split())
    join = ' '.join(merged)
    join_split = join.split()
    unique_split = np.unique(join_split)
    return unique_split


def get_model():
    # load the w2v model
    path_pretraind_model = '/Users/visanand2/Desktop/Pycharm/GoogleNews-vectors-negative300.bin'  # set as the path of pretraind model 
    model = KeyedVectors.load_word2vec_format(path_pretraind_model, binary=True)
    return model


def get_summed_vectors(merged_context, model):
    sum_vector = np.zeros(300)
    for keys in merged_context:
        try:
            sum_vector += model[keys]
        except:
            pass
    return sum_vector


def generate_similarity_matrix(df, model):
    embedding_dict = {}
    for index, meal in enumerate(df.meal):
        embedding_dict[meal] = get_summed_vectors(df.merged_context[index], model)
    embedding_df = pd.DataFrame(embedding_dict)

    similarity_matrix = cosine_similarity(embedding_df.T, embedding_df.T)
    similarity_matrix_df = pd.DataFrame(similarity_matrix, columns=embedding_df.columns, index=embedding_df.T.index)
    return similarity_matrix_df


def save_data(similarity_matrix_df):
    similarity_matrix_df.to_csv(
        "/Users/visanand2/Desktop/Pycharm/Recepie-Recommendation/fastapi_azure/similarity_matrix.csv")
    pd.DataFrame({"Meals": similarity_matrix_df.columns}).to_csv("Meals.csv", index=False)
    map_df = pd.DataFrame({"id": [data[i][0] + 1 for i in range(len(data))],
                           "meal": [data[i][1]["meal"] for i in range(len(data))],
                           "prep_time": [data[i][1]["prep_time"] for i in range(len(data))],
                           "region": [data[i][1]["region"] for i in range(len(data))]
                           })
    url = pd.read_csv("/Users/visanand2/Desktop/Pycharm/Recepie-Recommendation/scraper/Meals_slug.csv").reset_index()
    meal_url_mapper = pd.merge(map_df, url, left_on='id', right_on='index', how='left').drop(["index", "id"], axis=1)
    meal_url_mapper["url"] = meal_url_mapper.url.apply(lambda x: "https://gousto.co.uk" + x)
    meal_url_mapper.to_csv("/Users/visanand2/Desktop/Pycharm/Recepie-Recommendation/streamlit_app/meal_url_mapper.csv",
                           index=False)


if __name__ == '__main__':
    data = get_data()
    df = preprocess(data)
    df["processed_ingredients"] = df.ingredients.apply(lambda x: text_processing(x, "ingredients"))
    df["processed_meal"] = df.meal.apply(lambda x: text_processing(x, "meal"))
    df["merged_context"] = df.apply(lambda x: merge_context(x.processed_ingredients, x.processed_meal), axis=1)

    model = get_model()
    similarity_matrix_df = generate_similarity_matrix(df, model)

    save_data(similarity_matrix_df, )
