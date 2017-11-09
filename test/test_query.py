"""Unit Tests for queries"""
import query
import collections

Q = query.QueryProcessor(path='test/bin/', num_docs=5)

## BOOLEAN QUERIES
def test_standard_query():
    """Checks to make sure right results returned on simple query"""
    query = 'test'
    ans = [0, 1, 3, 4]
    assert ans == Q.query(query)

def test_phrase_query():
    """Checks to make sure right results returned on phrase query"""
    phrase_query = '\"third one\"'
    ans = [2]
    assert ans == Q.query(phrase_query)

def test_long_phrase_query():
    """Checks to make sure right results returned on phrase query"""
    phrase_query = '\"test document is here\"'
    ans = [1]
    assert ans == Q.query(phrase_query)

def test_and_query():
    """Checks to make sure right results returned on an AND query"""
    and_query = 'is test'
    ans = [0, 1]
    assert ans == Q.query(and_query)

def test_or_query():
    """Checks to make sure right results returned on an OR query"""
    or_query = 'test + document'
    ans = [0, 1, 3, 4]
    assert ans == Q.query(or_query)

def test_complex_query():
    """Checks to make sure right results returned on a complex query"""
    phrase_and_query = '\"test document\"+this'
    ans = [0, 1]
    assert ans == Q.query(phrase_and_query)

def test_query_normalizes():
    """Checks to make sure queries are normalized to match index"""
    normal_query = "goes"
    ans = [4]
    assert ans == Q.query(normal_query)

def test_query_not_in_index():
    """Checks to make sure queries with no results are handled properly"""
    not_in_index_query = "SPELLDRONG"
    ans = []
    assert ans == Q.query(not_in_index_query)

## RANKED QUERIES
def test_doc_retrieval_ranked_one():
    """Checking that each doc containing this term is returned"""
    query = "document"
    ans = {0, 1, 4}
    res = Q.query(query, ranked_flag=True)
    res = {i[0] for i in res}
    assert (ans == res)

def test_doc_retrieval_ranked_many():
    """Checking each doc containing these terms is returned"""
    query = "document test a"
    ans = {0, 1, 2, 3, 4}
    res = Q.query(query, ranked_flag=True)
    res = {i[0] for i in res}
    assert (ans == res)

import math
def test_most_relevant_first():
    """Manually calculating the high score for a term and checking
       that it is the first result"""
    query = "test"
    wqt = math.log(1 + 5/4)
    wdt = 1 + math.log(5)
    len_doc = math.sqrt(1+math.log(5, 2))
    res = Q.query(query, ranked_flag=True)
    score = wqt * wdt / len_doc
    assert res[0] == (3, score)
