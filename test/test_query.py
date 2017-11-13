"""Unit Tests for queries"""
import query
import math

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

## KGram Queries
def test_basic_kgram_query():
    """Testing basic end-of-word wildcard"""
    query = "thi*"
    ans = {0, 2}
    assert set(Q.query(query)) == ans

def test_star_at_front_kgram():
    """Testing basic start-of-word wildcard"""
    query = "*e"
    ans = {1, 2, 4}
    assert set(Q.query(query)) == ans

def test_multiple_stars():
    """Testing multiple wildcards"""
    query = "*cu*en*"
    ans = {0, 1, 4}
    assert set(Q.query(query)) == ans

def test_with_boolean():
    """Testing wildcard in a boolean"""
    query = "docu* here"
    ans = {1, 4}
    assert set(Q.query(query)) == ans

def test_not_in_vocab():
    """Testing query handles words not in corpus"""
    query = "teadjfkafadfadfcvbczz*"
    assert Q.query(query) == []

VOCAB = {'test', 'document', 'here', 'we', 'go', 'goe', 'anoth',
             'third', 'this', 'is', 'a', 'one'}

## Spelling Corrections
def test_spelling_correction_on_correct_query():
    """Testing spelling correction does nothing on correct query"""
    query = "test"
    assert Q.check_spelling(query, VOCAB) is None

def test_spelling_correction_one_word():
    """Testing spelling correction on single misspelled word"""
    query = "tesp"
    assert Q.check_spelling(query, VOCAB) == "test"

def test_spelling_correction_multiple_words():
    """Testing spelling correction on multiple words"""
    query = "test documant thard is"
    assert Q.check_spelling(query, VOCAB) == "test document third is"

def test_spelling_boolean_symbols():
    """Testing spelling correction on multiple words with boolean symbols"""
    query = '\"tesp documant herr\"+this'
    assert Q.check_spelling(query, VOCAB) == '\"test document here\"+this'

def test_spelling_weird_word():
    """Test spelling correction can handle impossible words"""
    query = "BV*%#@QDJZ"
    assert Q.check_spelling(query, VOCAB) is None

def test_spelling_ranked():
    query = "test documant herr"
    assert Q.check_spelling(query, VOCAB, ranked_flag=True) == "test document here"

def test_spelling_ranked_weird_word():
    query = "test dfkadfkahd"
    assert Q.check_spelling(query, VOCAB, ranked_flag=True) is None
