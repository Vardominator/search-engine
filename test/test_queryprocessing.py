"""Unit Tests for queries"""
import os
import json
import queryprocessing
import indexing

def process_documents():
    """Helper function to pre-process documents"""
    docs = []
    docs_dir = 'test/test_docs'

    for root,dirs,files in os.walk(docs_dir):
        files = sorted(files)

        for file in files:
            with open(os.path.join(docs_dir, file), 'r') as json_data:
                content = json.load(json_data)
                docs.append(content['body'])
    return docs

docs = process_documents() 

pos_index = indexing.create_index(docs)[0]

def test_standard_query():
    query = 'test'
    ans = [0, 1, 3, 4]
    literals = queryprocessing.process_query(query, None)
    assert ans == queryprocessing.query_search(literals, pos_index)

def test_phrase_query():
    phrase_query = '\"third one\"'
    literals = queryprocessing.process_query(phrase_query, None)
    queryprocessing.query_search(literals, pos_index)

def test_and_queries():
    and_query = 'test + document'
    literals = queryprocessing.process_query(and_query, None)
    queryprocessing.query_search(literals, pos_index)

def test_complex_query():
    phrase_and_query = '\"test document\"+this'
    literals = queryprocessing.process_query(phrase_and_query, None)
    queryprocessing.query_search(literals, pos_index)

# Testing wildcard queries
from kgram import KGramIndex
k_index = KGramIndex(3)
k_index.add_to_index(['test', 'best', 'tempest'])

def test_wildcard_handles_star_after():
    answer = {'test'}
    assert answer == queryprocessing.wildcard_query('tes*', k_index)

def test_handles_splitting_long_grams():
    answer = {'tempest'}
    assert answer == queryprocessing.wildcard_query('tempe*', k_index)

def test_wildcard_star_after():
    answer = {'best', 'test', 'tempest'}
    assert answer == queryprocessing.wildcard_query('*est', k_index)

def test_wildcard_small_grams():
    answer = {'test', 'best', 'tempest'}
    assert answer == queryprocessing.wildcard_query('*t', k_index)

def test_wildcard_middle_star():
    answer = {'test', 'tempest'}
    assert answer == queryprocessing.wildcard_query('te*t', k_index)

def test_wildcard_multiple_stars():
    answer = {'tempest'}
    assert answer == queryprocessing.wildcard_query('te*pe*t', k_index)
