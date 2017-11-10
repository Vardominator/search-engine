from itertools import chain
from operator import itemgetter
from collections import defaultdict
import numpy as np
import heapq
import re

from normalize import remove_special_characters

THRESHOLD = .31

class KGramIndex(object):
    """KGram Index that builds dictionaries of grams up to the designated
       number of grams. Each word added to the index is broken into grams
       from 1 to num_grams, and is added to the list for each gram. The
       index includes functions to retrieve words containing each of a
       list of grams."""

    def __init__(self, num_grams, vocab = None):
        self.num_grams = num_grams
        self.index = defaultdict(list)
        if vocab:
            self.add_to_index(vocab)

    def map_ngram(self, word):
        """Maps word to kgrams from 1 to k"""
        gram_word = "$" + word + "$"
        grams = map(set, [zip(*[gram_word[i:] for i in range(num_grams)]) for num_grams in range(1, self.num_grams+1)])
        for gram_set in grams:
            for gram in gram_set:
                gram_str = ''.join(gram)
                self.index[gram_str].append(word)

    def add_to_index(self, input_list):
        """Iterates through input list to construct kgram index"""
        if input_list:
            for word in input_list:
                self.map_ngram(word)

    def get_words(self, gram):
        """Returns a list of all words found containing kgram from index.
           Ensure that grams include '$' symbol"""
        if gram in self.index:
            return self.index[gram]
        else:
            return []

    def get_intersection_grams(self, grams):
        """Gets words that share the grams in common."""
        # Get a set of grams that are the correct size by either returning a gram or splitting it
        grams = set(chain(*[self.split_gram(gram) for gram in grams]))
        gram_sets = []
        for gram in grams:
            gram_sets.append(set(self.get_words(gram)))
        return set.intersection(*gram_sets)

    def split_gram(self, gram):
        """Splits a gram that is too long by returning a list of the largest subgrams"""
        if len(gram) <= self.num_grams:
            return [gram]
        max_len = self.num_grams
        return [gram[ind:ind+(max_len)] for ind in range(0, len(gram) - max_len + 1, 1)]

    def get_kgrams(self, word):
        """Gets grams from a word without adding to index"""
        gram_word = "$" + word + "$"
        all_grams = set()
        grams = map(set, [zip(*[gram_word[i:] for i in range(num_grams)]) for num_grams in range(1, self.num_grams+1)])
        for gram_set in grams:
            for gram in gram_set:
                all_grams.add(''.join(gram))
        return all_grams

    def find_spelling_candidate(self, qword, threshold):
        """Gets a spelling correction for a word by using the
           method described in class"""
        query_word_grams = self.get_kgrams(qword)
        candidates = set()
        for gram in query_word_grams:
            candidates |= set(self.get_words(gram))
        # ranked = sorted(candidates, key=lambda x: -self.calculate_jacard_coeff(query_word_grams, self.get_kgrams(x)))
        ranked = {word for word in candidates if self.calculate_jacard_coeff(query_word_grams, self.get_kgrams(word))>threshold}
        if ranked:
            return min([(word,self.edit_dist(qword, word)) for word in ranked], key=itemgetter(1))[0]

    def spelling_correction(self, query, vocab):
        """Returns a spelling-corrected query if necessary"""
        terms = re.findall("\w+", query)
        new_terms = [term if remove_special_characters(term) in vocab else self.find_spelling_candidate(term, THRESHOLD) for term in terms]
        if not terms == new_terms:
            if None in new_terms:
                return None
            for term, new in zip(terms, new_terms):
                if term != new:
                    query = query.replace(term, new)
            return query

    @staticmethod
    def calculate_jacard_coeff(qword_grams, tword_grams):
        n = len(qword_grams.intersection(tword_grams))
        return n / float(len(qword_grams) + len(tword_grams) - n)

    @staticmethod
    def edit_dist(qword, tword):
        """Calculates the Levenshtein edit distance
           between two words using Dynamic Programming"""
        if len(qword) < len(tword):
            return KGramIndex.edit_dist(tword, qword)
        if len(tword) == 0:
            return len(qword)
        qword = np.array(tuple(qword))
        tword = np.array(tuple(tword))
        previous_row = np.arange(tword.size + 1)
        for s in qword:
            current_row = previous_row + 1
            current_row[1:] = np.minimum(
                    current_row[1:],
                    np.add(previous_row[:-1], tword != s))
            current_row[1:] = np.minimum(
                    current_row[1:],
                    current_row[0:-1] + 1)
            previous_row = current_row
        return previous_row[-1]
