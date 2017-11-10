from flask import Flask, render_template, redirect, url_for,request
from flask import make_response
import json
import os
import time
import normalize
from diskindex import *
from query import *
from collections import defaultdict
import pickle

app = Flask(__name__)

pos_index = None
kgram_index = None
doc_id_files = {}

@app.route('/test', methods=['GET', 'POST'])
def home():
    """Used to test API."""
    return json.dumps({'response': "hello"})

@app.route('/buildindex', methods=['GET', 'POST'])
def buildindex():
    """Parse files of given directory, build in-memory index index, and return."""
    if request.method == 'POST':
        docs = []
        file_contents = {}
        docs_dir = request.form['corpus_dir']
        build_str = request.form['build']
        build = True if build_str == 'true' else False
        id = 0
        for root,dirs,files in os.walk(docs_dir):
            files = sorted(files)
            for file in files:
                doc_id_files[id] = file
                id += 1
                with open(os.path.join(docs_dir, file), 'r') as json_data:
                    content = json.load(json_data)
                    docs.append(content['body'])
                    file_contents[file] = {'body': content['body'],
                                           'title': content['title'],
                                           'url': content['url']}

        if build:
            indexwriter = IndexWriter()
            indexwriter.build_index(docs)

        queryprocessor = QueryProcessor(num_docs=len(files))
        diskindex = queryprocessor.disk_index
        vocab = diskindex.get_vocab()

        app.config['queryprocessor'] = queryprocessor
        app.config['diskindex'] = diskindex
        app.config['vocab'] = vocab
        app.config['file_contents'] = file_contents
        app.config['doc_id_files'] = doc_id_files
        return json.dumps({
                            'files': files,
                            'doc_count': len(files),
                            'terms': vocab,
                            'term_count': len(vocab)
                          })

@app.route('/showterms', methods=['GET', 'POST'])
def showterms():
    """Return terms of the index."""
    if request.method == 'POST':
        vocab = app.config['vocab']
        alphabet = defaultdict(list)
        for term in vocab:
            if term != "":
                alphabet[term[0]].append(term)
        return json.dumps({
                            'vocab': alphabet
                         })

@app.route('/query', methods=['GET', 'POST'])
def query():
    """Process user query and return relevant documents."""
    if request.method == 'POST':

        doc_id_files = app.config['doc_id_files']
        file_contents = app.config['file_contents']
        queryprocessor = app.config['queryprocessor']
        vocab = app.config['vocab']
        ranked_str = request.form['rankedRetrieval']

        query = request.form['query']
        ranked = True if ranked_str == 'true' else False
        search_results = queryprocessor.query(query, ranked)
        relevant_files = []
        relevant_contents = {}
        scores = []
        spell_corrected = queryprocessor.check_spelling(query, vocab)

        for result in search_results:
            if ranked:
                doc_id = result[0]
                scores.append(result[1])
            else:
                doc_id = result
            file = doc_id_files[doc_id]
            relevant_files.append(file)
            relevant_contents[file] = file_contents[file]

        return json.dumps({
                            'doc_ids': search_results,
                            'files': relevant_files,
                            'contents': relevant_contents,
                            'ranked': ranked,
                            'scores': scores,
                            'spell_corrected': spell_corrected
                          })


@app.route('/stem', methods=['GET', 'POST'])
def stem():
    """Return the stem of the word."""
    if request.method == 'POST':
        stemmed_term = normalize.stem(request.form['term'])
        print(stemmed_term)
        return json.dumps({
                            'term': request.form['term'],
                            'stemmed_term': stemmed_term
                          })

if __name__ == "__main__":
    app.run(debug = False)
