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
    answer = {'$te':['test'], '$t':['test'], "$":['test'], 'tes':['test'], 'te':['test'], 't':['test'],
              'est':['test'], 'es':['test'], 'e':['test'], 'st$':['test'], 'st':['test'], 's':['test'],
              't$':['test']}
    assert answer == kgram_test.index

def test_add_to_index():
    """Tests mapping over whole input list"""
    kgram_test = kgram.KGramIndex(3)
    kgram_test.add_to_index(TEST_LIST)
    answer = {'$te':['test', 'test2'], '$t':['test', 'test2'], '$':['test', 'test2', 'other'], 'tes':['test', 'test2'],
              'te':['test', 'test2'], 't':['test', 'test2', 'other'], 'est':['test', 'test2'], 'es':['test', 'test2'],
              'e':['test', 'test2', 'other'], 'st$':['test'], 'st':['test', 'test2'], 's':['test', 'test2'], 't$':['test'],
              'st2':['test2'], 't2$':['test2'], 't2':['test2'], '2':['test2'], '2$':['test2'], '$ot':['other'], '$o':['other'],
              'oth':['other'], 'ot':['other'], 'o':['other'], 'the':['other'], 'th':['other'], 'her':['other'], 'he':['other'],
              'h':['other'], 'er$':['other'], 'er':['other'], 'r$':['other'], 'r':['other'],
              }
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
