"""Unit Tests for special queries, should move over to queryprocessing later"""
import queryprocessing

# Bad practice importing kgram, need to mock call or something
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
