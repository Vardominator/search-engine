"""Unit tests for normalize.py"""
import normalize

def test_stem_stems():
    """Tests the stemmer on a single word"""
    test_word = 'ConSPIcuous'
    assert normalize.stem(test_word) == 'conspicu'

def test_remove_special_characters_removes_beg_end():
    """Tests that special characters are removed from the start and end"""
    test_word = "$!@'test%^"
    assert normalize.remove_special_characters(test_word) == 'test'

def test_remove_does_not_remove_middle():
    """Tests that special characters are not removed from the middle of words"""
    test_word = "te@#!st"
    assert normalize.remove_special_characters(test_word) == test_word

def test_remove_removes_apostrophes():
    """Tests that apostrophes are removed throughout word"""
    test_word = "'te's't'"
    assert normalize.remove_special_characters(test_word) == "test"

def test_dehyphenate_does_not_change_single_words():
    """Tests that dehyphenate does not affect un-hyphenated words"""
    test_word = "test"
    assert normalize.dehyphenate(test_word) == {test_word}

def test_dehyphenate_splits_correctly():
    """Tests that dehyphenate splits words correctly"""
    test_word = "test-test-check"
    answer = {test_word, "test", "check"}
    assert normalize.dehyphenate(test_word) == answer

def test_query_normalize_hyphens():
    """Tests that query normalization does not remove hyphens"""
    test_word = "TesT-HOUsE!!!"
    answer = "test-hous"
    assert normalize.query_normalize(test_word) == answer
