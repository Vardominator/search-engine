"""Normalization class"""
import re

from porter2stemmer import Porter2Stemmer

class Normalizer(object):
    def __init__(self):
        self.stemmer = Porter2Stemmer()

    def normalize(self, word):
        word = self.remove_special_characters(word)
        word_set = self.dehyphenate(word)
        word_set = [self.stem(token) for token in word_set]
        return word_set

    def stem(self, word):
        return self.stemmer.stem(word.lower())

    def remove_special_characters(self, word):
        word = re.sub(r'^\W+|\W+$', '', word)
        word = word.replace("'", "")
        return word

    def dehyphenate(self, word):
        if '-' not in word:
            return {word}
        else:
            word_list = word.split('-')
            word_list.append(word)
            return set(word_list)
