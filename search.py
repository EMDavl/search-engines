import json
import re

from pygtrie import StringTrie
import pymorphy2

from tokens import TokenType, Token
from tree_builder import TreeBuilder


class QueryParsingException(Exception):
    pass


def read_index():
    with open("index.txt", 'r', encoding='utf-8') as file:
        lines = file.readlines()
        tree = StringTrie()
        for line in lines:
            record = json.loads(line)
            tree[record["lemma"]] = record["words"]
        return tree


def print_help():
    print("""
    q - закончить выполнение
    h - получить справку о запросах
    <запрос> - получить список документов по запросу. Запрос может содержать AND / OR / NOT для уточнения и леммы для поиска.
    Общий вид запроса: <лемма> AND <лемма> OR (<лемма> OR <лемма>).
    AND имеет больший приоритет чем OR, выражение в скобках выполняется раньше того что вне
    """)


def parse_word(idx, string):
    russian_char = re.compile(r'[а-яА-Я]')
    word = ""
    while idx < len(string) and russian_char.match(string[idx]):
        word += string[idx]
        idx += 1
    return word


def is_operand(idx, query):
    if idx == len(query) - 1:
        return False
    if (query[idx: idx + 2]) == "OR":
        return True
    if idx == len(query) - 2:
        return False
    if query[idx: idx + 3] == "AND" or query[idx: idx + 3] == "NOT":
        return True
    return False


def extract_operand(idx, query):
    if (query[idx: idx + 2]) == "OR":
        return Token(TokenType.OPERATOR, "OR")
    if query[idx: idx + 3] == "AND":
        return Token(TokenType.OPERATOR, query[idx: idx + 3])
    if query[idx: idx + 3] == "NOT":
        return Token(TokenType.UNARY_OPERATOR, query[idx: idx + 3])


def parse(query):
    parsed = []
    russian_char = re.compile(r'[а-яА-Я]')
    idx = 0
    morph_analyzer = pymorphy2.MorphAnalyzer()
    while idx < len(query):
        char = query[idx]
        if char == '(':
            parsed.append(Token(TokenType.OP, char))
        elif char == ')':
            parsed.append(Token(TokenType.CP, char))
        elif char == ' ':
            idx += 1
            continue
        elif russian_char.match(char):
            word = parse_word(idx, query)
            parsed.append(Token(TokenType.LEXEME, morph_analyzer.normal_forms(word)[0]))
            idx = idx + len(word) - 1
        elif is_operand(idx, query):
            operand = extract_operand(idx, query)
            parsed.append(operand)
            idx = idx + len(operand.value) - 1
        else:
            raise QueryParsingException()
        idx += 1
    return parsed


def build_tree(parsed):
    tree_builder = TreeBuilder(parsed)
    return tree_builder.build()

def find_relevant_documents(tree, index_prefix_tree):
    return tree.eval(index_prefix_tree)


if __name__ == "__main__":
    try:
        index_prefix_tree = read_index()
    except Exception as e:
        print("Ошибка при чтении индекс-файла.", e)
        raise e

    quit_requested = False
    while not quit_requested:
        query = input("Введите запрос\n")
        if query == "q":
            quit_requested = True
        elif query == "h":
            print_help()
        else:
            # try:
            parsed = parse(query)
            tree = build_tree(parsed)
            print(tree)
            relevant_docs = find_relevant_documents(tree, index_prefix_tree)
            print(relevant_docs)