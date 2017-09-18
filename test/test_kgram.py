"""Unit test file for kgram.py"""
import kgram

TEST_LIST = ['test', 'test2', 'other']

def test_initialize_kgram():
    """Tests creation of class, asserts kgram # is assigned"""
    kgram_test = kgram.KGramIndex(2)
    assert kgram_test.num_grams == 2


def test_map_ngram_keys_created():
    """Tests kgram mapping with one word"""
    word = TEST_LIST[0]
    kgram_test = kgram.KGramIndex(3)
    kgram_test.map_ngram(word)
    answer = {'tes':['test'], 'est': ['test']}
    assert answer == kgram_test.index

def test_add_to_index():
    """Tests mapping over whole input list"""
    kgram_test = kgram.KGramIndex(3)
    kgram_test.add_to_index(TEST_LIST)
    answer = {'tes':['test', 'test2'], 'est':['test', 'test2'], 'st2':['test2'],
              'oth':['other'], 'the':['other'], 'her':['other']}
    assert kgram_test.index == answer

def test_add_to_index_null_list():
    """Tests that call to add_to_index handles empty list"""
    empty_list = []
    kgram_test = kgram.KGramIndex(3)
    kgram_test.add_to_index(empty_list)

def test_get_words_gets_words():
    """Tests that word retrieval works for initialized index"""
    kgram_test = kgram.KGramIndex(3)
    kgram_test.add_to_index(TEST_LIST)
    answer = {'test', 'test2'}
    assert set(kgram_test.get_words('est')) == answer

def test_get_words_handles_no_key():
    """Tests that no issues raised when calling missing key"""
    kgram_test = kgram.KGramIndex(3)
    kgram_test.get_words('not in index')
