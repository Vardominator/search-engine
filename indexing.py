import os
import collections

# POSITIONAL POSTING LIST
class PositionalPosting():
    def __init__(self, doc_id, positions=[]):
        # Initialize postings list for given document
        self.postings_list = (doc_id, positions)

    def add_position(self, position):
        # Add position index to respective postings list
        self.postings_list[1].append(position)


def create_index(corpus_dir, processed_docs):
    # CREATES POSITIONAL INVERTED INDEX
    pos_inv_index = {}

    # WALK THROUGH DOCUMENTS AND CREATE POSITIONAL INVERTED INDEX
    for document in sample_docs:
        terms = document.split()
        curr_term_position = 0

        for term in terms:
            if term not in pos_inv_index:
                pos_inv_index[term] = []
    
            posting_found = False
            if len(pos_inv_index[term]) == 0:
                pos_inv_index[term].append(PositionalPosting(sample_docs.index(document), [curr_term_position]))
        
            else:
                for posting in pos_inv_index[term]:
                    if posting.postings_list[0] == sample_docs.index(document):
                        posting_found = True
                        posting.postings_list[1].append(curr_term_position)
        
                if not posting_found:
                    pos_inv_index[term].append(PositionalPosting(sample_docs.index(document), [curr_term_position]))

            curr_term_position += 1

    # SORT DICTIONARY BY KEYS
    pos_inv_index = collections.OrderedDict(sorted(pos_inv_index.items(), key=lambda t:t[0])) 

    return pos_inv_index


def print_index(index):
    # PRINT DICTIONARY
    for key in index.keys():
        print("{}: ".format(key))
        for posting in index[key]:
            print(posting.postings_list)


if __name__ == "__main__":
    corpus_dir = 'data/documents'
    sample_docs = [ "hello you dumb fuck what blah blah blah is the mean life of life",
                    "fourscore and     seven years ago the dumb fuck made life possible",
                    "what is up the blah people are awesome     blah most of the time",
                    "time is precious unless you are studying blah liberal arts"]
    
    index = create_index(corpus_dir, sample_docs)
    # print_index(index)


