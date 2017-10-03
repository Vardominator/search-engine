import os
import collections
import shlex
import json
from time import time
import normalize
import queryprocessing
from kgram import KGramIndex

# VOCABULARY OF 
VOCAB = set()

class PositionalPosting():
    """Positional posting for each term in the Positional Inverted Index. 
       The posting is a tuple of the document id and the respective positions
       of the term in that document."""

    def __init__(self, doc_id, positions=[]):
        self.postings_list = (doc_id, positions)

    def add_position(self, position):
        self.postings_list[1].append(position)


def create_index(processed_docs):
    """Creates and returns the Positional Inverted Index and Kgram Index"""
    pos_inv_index = {}

    for i in range(len(processed_docs)):
        terms = processed_docs[i].split()
        curr_term_position = 0

        for word in terms:
            word = normalize.remove_special_characters(word)
            VOCAB.add(word)
            term_list = normalize.normalize(word)

            for term in term_list:
                if term not in pos_inv_index:
                    pos_inv_index[term] = []
                if len(pos_inv_index[term]) == 0:
                    pos_inv_index[term].append(PositionalPosting(i, [curr_term_position]))
                else:
                    last_posting = pos_inv_index[term][-1]
                    if last_posting.postings_list[0] == i:
                        last_posting.add_position(curr_term_position)
                    else:
                        pos_inv_index[term].append(PositionalPosting(i, [curr_term_position]))
            
            curr_term_position += 1

    pos_inv_index = collections.OrderedDict(sorted(pos_inv_index.items(), key=lambda t:t[0]))
    kgram_index = KGramIndex(3, VOCAB)
    return [pos_inv_index, kgram_index]