import os
import collections
import shlex

import queryprocessing

# POSITIONAL POSTING LIST
class PositionalPosting():
    def __init__(self, doc_id, positions=[]):
        # Initialize postings list for given document
        self.postings_list = (doc_id, positions)

    def add_position(self, position):
        # Add position index to respective postings list
        self.postings_list[1].append(position)


def create_index(processed_docs):
    # CREATES POSITIONAL INVERTED INDEX
    pos_inv_index = {}

    # WALK THROUGH DOCUMENTS AND CREATE POSITIONAL INVERTED INDEX
    for i in range(len(processed_docs)):
        terms = shlex.split(processed_docs[i])
        curr_term_position = 0
        for term in terms:
            if term not in pos_inv_index:
                pos_inv_index[term] = []
    
            posting_found = False
            if len(pos_inv_index[term]) == 0:
                pos_inv_index[term].append(PositionalPosting(i, [curr_term_position]))
            else:
                # CHECK IF EXISTS AT THE END OF THE LIST
                last_posting = pos_inv_index[term][-1]
                
                if last_posting.postings_list[0] == i:
                    last_posting.add_position(curr_term_position)
                else:
                    pos_inv_index[term].append(PositionalPosting(i, [curr_term_position]))

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
    test_docs_dir = 'data/testdocuments'
    sample_docs = []

    for root,dirs,files in os.walk(test_docs_dir):
        files = sorted(files)
        for file in files:
            with open(os.path.join(test_docs_dir, file), 'r') as f:
                sample_docs.append(f.read())

    index = create_index(sample_docs)
    # print_index(index)

    # TEST QUERY PROCESSOR

    # MUST RETURN [2,4,6]
    # literals = queryprocessing.process_query('\"Seven Years\" fuck asdfasd + awesome + crazy awesome')

    # MUST RETURN [1,2,4,6]
    # literals = queryprocessing.process_query('\"Seven Years\" fuck+ awesome + crazy awesome')

    # MUST RETURN [4]
    # literals = queryprocessing.process_query('crazy awesome')
    
    # MUST RETURN [0,1,5,6]
    literals = queryprocessing.process_query('\"dumb fuck\"')


    search_results = queryprocessing.query_search(literals, index)
    print(search_results)
    # print(search_results)