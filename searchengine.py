from flask import Flask, render_template, redirect, url_for,request
from flask import make_response
import json
import os

import indexing
import queryprocessing

app = Flask(__name__)

@app.route('/test', methods=['GET', 'POST'])
def home():
    return json.dumps({'response': "hello"})

@app.route('/buildindex', methods=['GET', 'POST'])
def buildindex():
    corpus_dir = 'data/documents'
    test_docs_dir = 'data/testdocuments'
    sample_docs = []

    for root,dirs,files in os.walk(test_docs_dir):
        files = sorted(files)
        for file in files:
            with open(os.path.join(test_docs_dir, file), 'r') as f:
                sample_docs.append(f.read())

    index = indexing.create_index(sample_docs)
    return json.dumps({'terms': list(index.keys())})

if __name__ == "__main__":
    app.run(debug = True)