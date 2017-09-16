import pytest
import kgram

def test_initialize_kgram():
    kgram_test = kgram.KGramIndex(2)
    assert kgram_test.num_grams == 2


def test_map_ngram_keys_created():
    word = "test"
    kgram_test = kgram.KGramIndex(3)
    answer = {"tes":["test"], "est": ["test"]}
    kgram_test.map_ngram(word)
    assert answer == kgram_test.index