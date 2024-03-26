from flask import Flask, render_template, request, jsonify

from vector_search import read_documents_tf_idf, convert_documents_to_vectors, query_to_vector, find_relevant_documents

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    query_vector = query_to_vector(query, unique_lemmas_idf)
    relevant_documents = find_relevant_documents(query_vector, documents_vectors)
    result = []
    for doc in relevant_documents[:10]:
        result.append((doc[0], documents_links[str(doc[0])]))
    return jsonify({
        'status': 'success',
        'query': query,
        'results': result
    })


@app.route('/file/<file_path>', methods=['GET'])
def get_page(file_path):
    return render_template(f'dir/file-{file_path}.html')


def get_links():
    file_path = "res.txt"
    dict = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()
        lines = data.splitlines()
        for line in lines:
            temp = line.split()
            dict[temp[0]] = temp[1]
    return dict


if __name__ == '__main__':
    documents_tf_idf, unique_lemmas_idf = read_documents_tf_idf()
    documents_vectors = convert_documents_to_vectors(documents_tf_idf, unique_lemmas_idf)
    documents_links = get_links()
    app.run(debug=True)
