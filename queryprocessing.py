import shlex
from itertools import chain, groupby
from operator import itemgetter
from specialqueries import special_queries
import normalize

import time

def process_query(query):
    if query.startswith(':'):
        special_queries(query[1:])
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
