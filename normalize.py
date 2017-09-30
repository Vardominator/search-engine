"""Normalization module"""
import re

import stemming.porter2


def normalize(word):
    """Main function to normalize words, removes any special characters
       from beginning and end of word, breaks the word into a set if it
       contains a hyphen, and stems each word using the Porter2Stemmer"""
    word_set = dehyphenate(word)
    word_list = [stem(token) for token in word_set]
    return word_list


def stem(word):
    return stemming.porter2.stem(word.lower())


def remove_special_characters(word):
    """Removes any special characters from the beginning and end of the
       word, and gets rid of any apostrophe throughout."""
    word = re.sub(r'^\W+|\W+$', '', word)
    word = word.replace("'", "")
    return word.lower()


def dehyphenate(word):
    """Checks for words with hyphens and breaks them into a set of the
       word and each subword split between the hyphens. Returns a set"""
    if '-' not in word:
        return {word}
    else:
        word_list = word.split('-')
        word_list.append(word)
        return set(word_list)

def query_normalize(word):
    """Removes special characters and stems words without dehyphenating,
       which is necessary for queries"""
    word = remove_special_characters(word)
    word = stem(word)
    return word
