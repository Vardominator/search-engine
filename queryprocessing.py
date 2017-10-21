import shlex
import sys
import time
import math
import heapq
from collections import defaultdict
from itertools import chain, groupby
from operator import itemgetter
import normalize
from kgram import KGramIndex

def process_query(query, kgram_index):
    """Isolate query literals"""
    if '*' in query:
        literals = wildcard_query(query, kgram_index)
    else:
        literals = query.split('+')
        literals = list(map(str.strip, literals))
    return literals

def query_search(literals, index):
    """Searches index for literals in query. Merges results of each literal."""
    succes_doc_ids = []

    for literal in literals:
        # SKILL LITERAL IF ALL TERMS DO NOT EXIST IN THE INDEX
        all_terms = literal.replace('"', '').split()
        all_terms = [normalize.query_normalize(term) for term in all_terms]
        if not all(term in index for term in all_terms):
            continue       

        queries = shlex.split(literal)
        docs_with_all_queries = []

        for subliterals in queries:
            # SPLIT IF PHRASE CONTAINS MULTIPLE WORDS
            subliterals = subliterals.split()
            # NORMALIZE TERMS IN PHRASE
            subliterals = [normalize.query_normalize(term) for term in subliterals]
            
            # COMBINE POSITIONAL POSTING OBJECTS FOR A LITERAL
            combined_postings = list(chain.from_iterable([index[subliteral] for subliteral in subliterals]))
            # EXTRACT POSTINGS LISTS FOR EVERY POSITIONAL POSTING OBJECT
            combined_postings_lists = [posting.postings_list for posting in combined_postings]
            # SORT LISTS BY DOCUMENT ID
            combined_postings_lists = sorted(combined_postings_lists, key=lambda t:t[0])

            docs_with_current_query = []

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

                            if len(left_list) != 1 and len(right_list) != 1:
                                while i < len(left_list) - 1 and j < len(right_list) - 1:
                                    if left_list[i] < right_list[j] and left_list[i] + 1 != right_list[j]:
                                        i += 1
                                    elif left_list[i] + 1 == right_list[j]:
                                        break
                                    else:
                                        j += 1
                            elif len(right_list) == 1:
                                for k in range(len(left_list) - 1):
                                    if left_list[k] + 1 == right_list[0]:
                                        break
                                    i += 1
                            elif len(left_list) == 1:
                                for k in range(len(right_list) - 1):
                                    if left_list[0] + 1 == right_list[k]:
                                        break
                                    j += 1

                            if left_list[i] + 1 != right_list[j]:
                                subliteral_found = False
                                break

                        if subliteral_found:
                            docs_with_current_query.append(doc_postings[0][0])

                else:
                    docs_with_current_query.append(doc_postings[0][0])

            docs_with_all_queries.append(docs_with_current_query)

        # INTERSECT DOC IDs WITH SUCCESSFUL QUERIES
        ids_intersect = list(set.intersection(*map(set, docs_with_all_queries)))
        succes_doc_ids.extend(ids_intersect)

    return sorted(set(succes_doc_ids))


def wildcard_query(query, kgram_index):
    """Puts queries in correct form for the kgram index, splits on grams
       and returns the strings that contain each gram"""
    if not query.startswith('*'):
        query = '$' + query
    if not query.endswith('*'):
        query = query + '$'
    gram_list = query.split('*')
    gram_list = set(filter(None, gram_list))
    return kgram_index.get_intersection_grams(gram_list)


def ranked_query(query, k, index):
    """Returns the k most relevant documents from the corpus for a query,
       using the "term at a time" algorithm"""
    A = defaultdict(int)
    heap = []
    query = [query_normalize(word) for word in query.split()]
    for term in query:
        wqt = math.log(1 + len(index)/len(index[term]))
        for posting in index[term]:
            wdt = 1 + math.log(len(postings[1]))
            A[postings[0]] += wdt * wqt
    for doc, score in A.items():
        heapq.heappush(heap, (-score, doc))
    return [key for value, key in heapq.nsmallest(k, heap)]
