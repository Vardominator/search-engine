"""Normalization module"""
import re

from porter2stemmer import Porter2Stemmer

STEMMER = Porter2Stemmer()

def normalize(word):
    word = remove_special_characters(word)
    word_set = dehyphenate(word)
    word_set = [stem(token) for token in word_set]
    return word_set


def stem(word):
    return STEMMER.stem(word.lower())


def remove_special_characters(word):
    word = re.sub(r'^\W+|\W+$', '', word)
    word = word.replace("'", "")
    return word


def dehyphenate(word):
    if '-' not in word:
        return {word}
    else:
        word_list = word.split('-')
        word_list.append(word)
        return set(word_list)
