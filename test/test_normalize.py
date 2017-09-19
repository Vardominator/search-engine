"""Unit tests for normalize.py"""
import normalize

def test_stem_stems():
    test_word = 'ConSPIcuous'
    assert normalize.stem(test_word) == 'conspicu'

def test_remove_special_characters_removes_beg_end():
    test_word = "$!@'test%^"
    assert normalize.remove_special_characters(test_word) == 'test'

def test_remove_does_not_remove_middle():
    test_word = "te@#!st"
    assert normalize.remove_special_characters(test_word) == test_word

def test_remove_removes_apostrophes():
    test_word = "'te's't'"
    assert normalize.remove_special_characters(test_word) == "test"

def test_dehyphenate_does_not_change_single_words():
    test_word = "test"
    assert normalize.dehyphenate(test_word) == {test_word}

def test_dehyphenate_splits_correctly():
    test_word = "test-test-check"
    answer = {test_word, "test", "check"}
    assert normalize.dehyphenate(test_word) == answer
