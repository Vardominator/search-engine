import shlex
import sys
from itertools import chain, groupby
from operator import itemgetter

import normalize
from kgram import KGramIndex

def process_query(query, kgram_index = None):
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

        all_terms = literal.replace('"', '').split()
        all_terms = [normalize.query_normalize(word) for word in all_terms]
        queries_found = 0
        # all_terms = [normalize.normalize(term) for term in all_terms]
        # SKIP IF ALL TERMS IN SUBLITERAL ARE NOT IN INDEX
        if not all(term in index for term in all_terms):
            continue

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

            docs_with_current_query = []
            found_count = 0
            # SPLIT POSTINGS BY DOCUMENT ID
            for key,doc_postings in groupby(combined_postings_lists, itemgetter(0)):
                doc_postings = list(doc_postings)

                if len(subliterals) > 1:
                    # CHECK IF LENGTH OF POSTINGS IS THE SAME AS THE SUBLITERALS
                    if len(doc_postings) == len(subliterals):
                        posting_lists = [posting[1] for posting in doc_postings]
                        subliteral_found = True

                        for a in range(len(posting_lists) - 1):
                            left_list = posting_lists[a]
                            right_list = posting_lists[a + 1]

                            i = 0
                            j = 0

                            while i < len(left_list) - 1:
                                increment_found = False
                                if left_list[i] < right_list[j] and left_list[i] + 1 != right_list[j]:
                                    i += 1
                                elif left_list[i] + 1 == right_list[j]:
                                    increment_found = True
                                    break
                                else:
                                    if j < len(right_list) - 1:
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


# Unsure if we need to pass KGramIndex after moving these functions around, but this works for now
def wildcard_query(query, kgram_index):
    if not query.startswith('*'):
        query = '$' + query
    if not query.endswith('*'):
        query = query + '$'
    gram_list = query.split('*')
    gram_list = set(filter(None, gram_list))
    return kgram_index.get_intersection_grams(gram_list)
