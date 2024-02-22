import itertools
import json
from typing import Dict

from bs4 import BeautifulSoup
import os
import re
import pymorphy2

flatten = itertools.chain.from_iterable


def download_htmls():
    folder_path = "dir"
    files = os.listdir(folder_path)
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


def divide_into_words(texts):
    words = {}
    for i in range(len(texts)):
        word_pattern = re.compile(r'\b[а-яА-Я]+\b')
        extracted_words = word_pattern.findall(texts[i])
        for word in extracted_words:
            if word in words:
                words[word].add(i + 1)
            else:
                words[word] = {i + 1, }
    return words


def group_word_by_lemma(words: Dict[str, set[int]]) -> Dict[str, list[tuple[str, set[int]]]]:
    title_group_words = {}
    morph = pymorphy2.MorphAnalyzer()
    for word in words.keys():
        lemma = morph.parse(word)[0].normal_form
        if lemma in title_group_words:
            title_group_words[lemma].append((word, words[word]))
        else:
            title_group_words[lemma] = [(word, words[word])]
    return title_group_words


def save_words_to_file(words):
    with open('tokens.txt', 'w', encoding='utf-8') as file:
        for word in words.keys():
            file.write(str(word) + '\n')


def save_lemma_words_to_file(title_group_words: Dict[str, list[tuple[str, set[int]]]]):
    with open('lemma.txt', 'w', encoding='utf-8') as file:
        for lemma in title_group_words:
            file.write(lemma + ': ')
            for index, word in enumerate(title_group_words[lemma]):
                if index < len(title_group_words[lemma]) - 1:
                    file.write(word[0])
                else:
                    file.write(word[0])
            file.write('\n')


def save_lemma_to_index(title_group_words: Dict[str, list[tuple[str, set[int]]]]):
    with open('index.txt', 'w', encoding='utf-8') as file:
        for lemma in title_group_words:
            record = {
                "lemma": f"{lemma}",
                "words": list(set(flatten(map(lambda w: w[1], title_group_words[lemma]))))
            }
            json.dump(record, file, ensure_ascii=False)
            file.write('\n')


if __name__ == '__main__':
    htmls = download_htmls()
    texts = extract_text_from_html(htmls)
    words: Dict[str, set[int]] = divide_into_words(texts)
    save_words_to_file(words)
    title_group_words = group_word_by_lemma(words)
    save_lemma_words_to_file(title_group_words)
    save_lemma_to_index(title_group_words)
