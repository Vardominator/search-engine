import os
import collections
import shlex
import json
from time import time
import normalize
import queryprocessing
from kgram import KGramIndex

VOCAB = set()

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

    t0 = time()
    # WALK THROUGH DOCUMENTS AND CREATE POSITIONAL INVERTED INDEX
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
                    # CHECK IF EXISTS AT THE END OF THE LIST
                    last_posting = pos_inv_index[term][-1]

                    if last_posting.postings_list[0] == i:
                        last_posting.add_position(curr_term_position)
                    else:
                        pos_inv_index[term].append(PositionalPosting(i, [curr_term_position]))

            curr_term_position += 1

    # SORT DICTIONARY BY KEYS
    pos_inv_index = collections.OrderedDict(sorted(pos_inv_index.items(), key=lambda t:t[0]))
    t1 = time()
    print("Time to build pos index: {}".format(t1-t0))
    kgram_index = KGramIndex(3, VOCAB)
    t2 = time()
    print("Time to build indexes: {}".format(t2-t0))
    return [pos_inv_index, kgram_index]


def print_index(index):
    # PRINT DICTIONARY
    for key in index.keys():
        print("{}: ".format(key))
        for posting in index[key]:
            print(posting.postings_list)

if __name__ == "__main__":
    docs_dir = 'data/documents'
    test_docs_dir = 'data/documents'
    docs = []

    id = 0

    for root,dirs,files in os.walk(docs_dir):
        files = sorted(files, key=lambda x: int(os.path.splitext(x)[0]))
        for file in files:
            # doc_id_files[id] = file
            id += 1
            with open(os.path.join(docs_dir, file), 'r') as json_data:
                content = json.load(json_data)
                docs.append(content['body'])
                # file_contents[file] = {'body': content['body'],
                #                         'title': content['title'],
                #                         'url': content['url']}


    indexes = create_index(docs)

    # print(index['annual'])
    # TEST QUERY PROCESSOR

    # MUST RETURN [2,4,6]
    # literals = queryprocessing.process_query('\"Seven Years\" fuck asdfasd + awesome + crazy awesome')

    # MUST RETURN [1,2,4,6]
    # literals = queryprocessing.process_query('\"Seven Years\" fuck+ awesome + crazy awesome')

    # MUST RETURN [4]
    # literals = queryprocessing.process_query('crazy awesome')

    # MUST RETURN [0,1,5,6]
    # literals = queryprocessing.process_query('\"dumb fuck\"')

    # MUST RETURN [1,5,6]
    # literals = queryprocessing.process_query('\"dumb fuck\" ago')

    # literals = queryprocessing.process_query('asdfasdf')
    # literals = queryprocessing.process_query('nano')

    # MUST RETURN [7]
    # literals = queryprocessing.process_query(':stem conspicuous')
    # print(literals)
    # if literals:
    #     search_results = queryprocessing.query_search(literals, index)
    #     print(search_results)
    # print(search_results)

    literals = queryprocessing.process_query('\"The map at left shows the tracts in relation to each other\" + \"acquisition of florida power\" everglades + \"read a variety of stories that tell about soldiers\" + \"nps central\"', indexes[1])
    search_results = queryprocessing.query_search(literals, indexes[0])
    print(search_results)
