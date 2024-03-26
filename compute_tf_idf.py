import math
import os
import re
from bs4 import BeautifulSoup
import pymorphy2

DOCUMENTS_NUM = 121

def download_htmls():
    folder_path = "templates/dir"
    pattern = re.compile("\d+")
    files = sorted(os.listdir(folder_path), key=lambda x: int(pattern.findall(x)[0]))

    html_files = []
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        if file_path.endswith(".html"):
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            html_files.append(html_content)
    return html_files


def extract_text_from_html(htmls):
    texts = []
    for html in htmls:
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        texts.append(text)
    return texts


def save_to_file(is_lemma, item, index, total, item_document_count):
    if is_lemma == True:
        filename = f"tf-idf-lemma/tf-idf-{index}.txt"
    else:
        filename = f"tf-idf-tokens/tf-idf-{index}.txt"
    with open(filename, 'w', encoding='utf-8') as file:
        for item, key in item.items():
            tf = key / total
            idf = math.log(DOCUMENTS_NUM / item_document_count[item])
            if_idf = tf * idf
            file.write(str(item) + ' ' + str(format(idf, '.4f')) + ' ' + str(format(if_idf, '.4f')) + '\n')


def calculate_word_count(texts):
    words_html_count = []
    words_document_count = {}
    total_words = []
    for index, text in enumerate(texts):
        words_html_count.append({})
        total_words.append(0)
        word_pattern = re.compile(r'\b[а-яА-Я]+\b')
        extracted_words = word_pattern.findall(text)
        for word in extracted_words:
            if word in words_html_count[index]:
                words_html_count[index][word] += 1
            else:
                words_html_count[index][word] = 1
                if word in words_document_count:
                    words_document_count[word] += 1
                else:
                    words_document_count[word] = 1
            total_words[index] += 1
    return words_html_count, words_document_count, total_words


def calculate_lemma_count(words_html_count):
    lemma_html_count = []
    lemma_document_count = {}
    morph = pymorphy2.MorphAnalyzer()
    for index, html_words in enumerate(words_html_count):
        lemma_html_count.append({})
        for word, key in html_words.items():
            lemma = morph.parse(word)[0].normal_form
            if lemma in lemma_html_count[index]:
                lemma_html_count[index][lemma] += key
            else:
                lemma_html_count[index][lemma] = key
                if lemma in lemma_document_count:
                    lemma_document_count[lemma] += 1
                else:
                    lemma_document_count[lemma] = 1
    return lemma_html_count, lemma_document_count


if __name__ == '__main__':
    words_htmls_count = {}
    htmls = download_htmls()
    texts = extract_text_from_html(htmls)

    words_html_count, words_document_count, total_words = calculate_word_count(texts)
    for index, words in enumerate(words_html_count):
        save_to_file(False, words, index, total_words[index], words_document_count)

    lemma_html_count, lemma_document_count = calculate_lemma_count(words_html_count)
    for index, lemma in enumerate(lemma_html_count):
        save_to_file(True, lemma, index, total_words[index], lemma_document_count)
