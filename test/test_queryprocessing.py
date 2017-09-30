"""Unit Tests for queries"""
import queryprocessing
from indexing import PositionalPosting
import collections

sample_index = {
              "test":[PositionalPosting(0,[3]),
                      PositionalPosting(1,[1]),
                      PositionalPosting(3,[0, 1, 2, 3, 4]),
                      PositionalPosting(4,[1])],
              "document":[PositionalPosting(0,[4]),
                          PositionalPosting(1,[2]),
                          PositionalPosting(4,[0])],
              "here":[PositionalPosting(1,[4]),
                      PositionalPosting(2,[0]),
                      PositionalPosting(4,[3])],
              "we":[PositionalPosting(2,[1])],
              "go":[PositionalPosting(2,[2])],
              "goe":[PositionalPosting(4,[2])],
              "anoth":[PositionalPosting(1,[0])],
              "third":[PositionalPosting(2,[4])],
              "this":[PositionalPosting(0,[0])],
              "is":[PositionalPosting(0,[1]),
                      PositionalPosting(1,[3])],
              "a":[PositionalPosting(0,[2]),
                      PositionalPosting(2,[3])],
              "one":[PositionalPosting(2,[5])]
             }
pos_index = collections.OrderedDict(sorted(sample_index.items(), key=lambda t:t[0]))

def test_standard_query():
    query = 'test'
    ans = [0, 1, 3, 4]
    literals = queryprocessing.process_query(query, None)
    assert ans == queryprocessing.query_search(literals, pos_index)

def test_phrase_query():
    phrase_query = '\"third one\"'
    ans = [2]
    literals = queryprocessing.process_query(phrase_query, None)
    assert ans == queryprocessing.query_search(literals, pos_index)

def test_and_queries():
    and_query = 'test + document'
    ans = [0, 1, 3, 4]
    literals = queryprocessing.process_query(and_query, None)
    assert ans == queryprocessing.query_search(literals, pos_index)

def test_complex_query():
    phrase_and_query = '\"test document\"+this'
    ans = [0, 1]
    literals = queryprocessing.process_query(phrase_and_query, None)
    assert ans == queryprocessing.query_search(literals, pos_index)

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
