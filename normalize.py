"""Normalization class"""
from porter2stemmer import Porter2Stemmer
from string import punctuation
import re

class Normalizer(object):
    def __init__(self):
        self.stemmer = Porter2Stemmer()

    def normalize(self, word):
        word = self.remove_special_characters(word)
        word_list = self.dehyphenate(word)
        for token in word_list:
            token = self.stem(token)
        return word_list

    def stem(self, word):
        return self.stemmer.stem(word.lower())

    def remove_special_characters(self, word):
        word = re.sub(r'^\W+|\W+$', '', word)
        word = word.replace("'","")
        return word

    def dehyphenate(self, word):
        if '-' not in word:
            return [word]
        else:
            word_list = word.split('-')
            word_list.append(word)
            return set(word_list.append(word))
