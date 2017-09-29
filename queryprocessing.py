import shlex
import sys
from itertools import chain, groupby
from operator import itemgetter

import normalize
from kgram import KGramIndex

<<<<<<< HEAD
import time

def process_query(query):
=======
def process_query(query, kgram_index = None):
>>>>>>> a15a16df9a8745bce6ad1b07a7c77ae1a9a5f4ae
    if query.startswith(':'):
        special_queries(query[1:])
    else:
        if '*' in query:
            literals = wildcard_query(query, kgram_index)
        else:
            literals = query.split('+')
            literals = list(map(str.strip, literals))
        return literals

def query_search(literals, index):
    succes_doc_ids = []

    for literal in literals:
        queries = shlex.split(literal)
        
        docs_with_all_queries = []

        for subliterals in queries:
            # SPLIT IF PHRASE CONTAINS MULTIPLE WORDS
            subliterals = subliterals.split()

            subliterals = [normalize.query_normalize(term) for term in subliterals]

            # COMBINE POSITIONAL POSTING OBJECTS FOR A LITERAL
            combined_postings = list(chain.from_iterable([index[subliteral] for subliteral in subliterals]))
            # EXTRACT POSTINGS LISTS FOR EVERY POSITIONAL POSTING OBJECT
            combined_postings_lists = [posting.postings_list for posting in combined_postings]

            # SORT LISTS BY DOCUMENT ID
            combined_postings_lists = sorted(combined_postings_lists, key=lambda t:t[0])
<<<<<<< HEAD
            
=======
>>>>>>> a15a16df9a8745bce6ad1b07a7c77ae1a9a5f4ae

            docs_with_current_query = []
            found_count = 0
            # SPLIT POSTINGS BY DOCUMENT ID

            for key,doc_postings in groupby(combined_postings_lists, itemgetter(0)):
                doc_postings = list(doc_postings)

                if len(subliterals) > 1:
                    # CHECK IF LENGTH OF POSTINGS IS THE SAME AS THE SUBLITERALS
                    if len(doc_postings) == len(subliterals):
                        subliteral_found = True

                        for a in range(len(doc_postings) - 1):
                            left_list = doc_postings[a][1]
                            right_list = doc_postings[a + 1][1]
                            i = 0
                            j = 0

                            # if len(left_list) != 1 and len(right_list) != 1:
                            while i < len(left_list) - 1 and j < len(right_list) - 1:
                                if left_list[i] < right_list[j] and left_list[i] + 1 != right_list[j]:
                                    i += 1
                                elif left_list[i] + 1 == right_list[j]:
                                    break
                                else:
                                    j += 1

                            if left_list[i] + 1 != right_list[j]:
                                subliteral_found = False
                                break

                        if subliteral_found:
                            docs_with_current_query.append(doc_postings[0][0])

                else:
                    docs_with_current_query.append(doc_postings[0][0])

            docs_with_all_queries.append(docs_with_current_query)

        # UNIONIZE DOC IDs WITH SUCCESSFUL QUERIES
        ids_intersect = list(set.intersection(*map(set, docs_with_all_queries)))
        succes_doc_ids.extend(ids_intersect)

    return sorted(set(succes_doc_ids))


def special_queries(query):
    if query == 'q':
        sys.exit()
    elif query.startswith('stem '):
        if len(query) > 5:
            word = query[5:]
            print('Stemming word {}:'.format(word))
            print(normalize.stem(word))
        else:
            print('Please provide a word with the stem command.')
            print('e.g., >>>:stem word')
    elif query.startswith('index '):
        if len(query) > 6:
            print('Indexing folder {}:'.format(query[6:]))
        else:
            print('Please provide a directory name with the index command.')
            print('e.g., >>>:index target_folder')
    elif input == 'vocab':
        print('Printing all terms in the vocabulary:')
    else:
        print('Unrecognized command')


def wildcard_query(query, kgram_index):
    if not query.startswith('*'):
        query = '$' + query
    if not query.endswith('*'):
        query = query + '$'
    gram_list = query.split('*')
    gram_list = set(filter(None, gram_list))
    return kgram_index.get_intersection_grams(gram_list)
