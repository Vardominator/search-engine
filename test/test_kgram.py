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

def test_get_kgrams():
    word = "word"
    ans = {'$', 'w', 'o', 'r', 'd', '$w', 'wo', 'or', 'rd', 'd$',
           '$wo', 'wor', 'ord', 'rd$'}
    kgram_test = kgram.KGramIndex(3)
    assert kgram_test.get_kgrams(word) == ans

def test_jacard():
    """Manually calculating jacard and comparing with results of function"""
    kgram_test = kgram.KGramIndex(3)
    word = kgram_test.get_kgrams("word")
    other = kgram_test.get_kgrams("ward")
    # Manual calculation
    print(word.intersection(other))
    print(word.union(other))
    intersec = 8
    w_gram = 14
    a_gram = 14
    ans = intersec / (14 + 14 - intersec)
    assert kgram_test.calculate_jacard_coeff(word, other) == ans

def test_edit_dist():
    """Checking edit distance between two words"""
    word = "word"
    other = "wart"
    assert kgram.KGramIndex.edit_dist(word, other) == 2

def test_all_min_edits():
    """Checking all terms with minimum edit distance returned"""
    word = "iest"
    vocab = ['west', 'best', 'bar']
    kgram_test = kgram.KGramIndex(3)
    assert set(kgram_test.all_min_edits(vocab, word)) == {'west', 'best'}

def test_find_spelling_candidate():
    """Checking correct result for one spelling correction"""
    word = "wort"
    vocab = ['word', 'ward', 'bar']
    threshold = .3
    kgram_test = kgram.KGramIndex(3)
    kgram_test.add_to_index(vocab)
    assert kgram_test.find_spelling_candidates(word, threshold) == ['word']

def test_find_spelling_two_candidates():
    """Checking find spelling returns all candidates with min edit distance"""
    word = "iest"
    vocab = ['west', 'best', 'bar']
    thresh = .31
    kgram_test = kgram.KGramIndex(3)
    kgram_test.add_to_index(vocab)
    assert set(kgram_test.find_spelling_candidates(word, thresh)) == {'west', 'best'}

def find_spelling_no_candidates():
    """Checking find spelling handles impossible words"""
    word = "fgdaggd"
    vocab = ['west', 'best', 'bar']
    thresh = .31
    kgram_test = kgram.KGramIndex(3)
    kgram_test.add_to_index(vocab)
    assert set(kgram_test.find_spelling_candidates(word, thresh)) == []
