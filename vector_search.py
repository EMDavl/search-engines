import re
import os
import pymorphy2
import numpy as np


def read_documents_tf_idf():
    folder_path = "tf-idf-lemma"
    pattern = re.compile("\d+")
    files = sorted(os.listdir(folder_path), key=lambda x: int(pattern.findall(x)[0]))

    documents_tf_idf = []
    unique_lemmas_idf = {}
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        if file_path.endswith(".txt"):
            dict = {}
            with open(file_path, 'r', encoding='utf-8') as file:
                data = file.read()
                lines = data.splitlines()
                for line in lines:
                    temp = line.split()
                    if temp[0] not in unique_lemmas_idf:
                        unique_lemmas_idf[temp[0]] = float(temp[1])
                    dict[temp[0]] = float(temp[2])
            documents_tf_idf.append(dict)
    return documents_tf_idf, unique_lemmas_idf


def parse(query):
    russian_char = re.compile(r'[а-яА-Я]')
    morph_analyzer = pymorphy2.MorphAnalyzer()
    words = query.split(" ")
    tokens = {}
    for word in words:
        if russian_char.match(word):
            normal_forms = morph_analyzer.normal_forms(word)[0]
            if normal_forms in tokens:
                tokens[normal_forms] += 1
            else:
                tokens[normal_forms] = 1
    return tokens

def query_to_vector(query, unique_lemmas_idf):
    parsed = parse(query)
    tf_idf = calculate_tf_idf(parsed, unique_lemmas_idf)
    zeros_vector = np.zeros(len(unique_lemmas_idf))
    for index, lemma in enumerate(unique_lemmas_idf):
        if lemma in tf_idf:
            zeros_vector[index] = tf_idf[lemma]
    return zeros_vector

def calculate_tf_idf(parsed_query, unique_lemmas_idf):
    tf_idf = {}
    length = len(parsed_query)
    for token in parsed_query.keys():
        tf_idf[token] = (parsed_query[token] / length) * unique_lemmas_idf[token]
    return tf_idf

def find_relevant_documents(query_vector, documents_vectors):
    result = []
    for index, document_vector in enumerate(documents_vectors):
        similarity = calculate_cosine_similarity(document_vector, query_vector)
        result.append((index + 1, similarity))

    sorted_result = sorted(result, key=lambda x: x[1], reverse=True)
    return sorted_result

def calculate_cosine_similarity(vector1, vector2):
    return np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))

def convert_documents_to_vectors(documents_tf_idf, unique_lemmas_idf):
    documents_vectors = []
    for document in documents_tf_idf:
        zeros_vector = np.zeros(len(unique_lemmas_idf))
        for index, lemma in enumerate(unique_lemmas_idf):
            if lemma in document:
                zeros_vector[index] = document[lemma]
        documents_vectors.append(zeros_vector)
    return documents_vectors


if __name__ == "__main__":
    documents_tf_idf, unique_lemmas_idf = read_documents_tf_idf()
    documents_vectors = convert_documents_to_vectors(documents_tf_idf, unique_lemmas_idf)

    quit_requested = False
    while not quit_requested:
        query = input("Введите запрос\n")
        if query == "q":
            quit_requested = True
        else:
            query_vector = query_to_vector(query, unique_lemmas_idf)
            result = find_relevant_documents(query_vector, documents_vectors)
            print("Топ 10 найденных результатов по введенному запросу:")
            for document in result[:10]:
                print(document[0])
