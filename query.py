import heapq
import math
import pickle
import shlex
import struct
import re
from collections import defaultdict
from itertools import chain, groupby
from operator import itemgetter

from kgram import KGramIndex
from diskindex import DiskIndex
from normalize import query_normalize, remove_special_characters
from utils import intersect_sorted_lists, union_sorted_lists

THRESHOLD = .35

class QueryProcessor(object):
    """Query processing class, creates an interface to on-disk index
       and kgram index for queries. Supports boolean and ranked queries,
       and handles spelling corrections using kgram index"""

    def __init__(self, path='bin/', num_docs=0):
        with open('{}kgram.bin'.format(path), 'rb') as f:
            self.kgram_index = pickle.load(f)
        self.disk_index = DiskIndex(path)
        self.k_docs = 10
        self.num_docs = num_docs
        self.path = path

    def query(self, query, ranked_flag=False):
        """Query interface, returns results of either boolean or ranked queries"""
        if ranked_flag:
            return self.ranked_query(query, self.k_docs)
        return self.boolean_query(query)

    def check_spelling(self, query, vocab, ranked_flag=False):
        """Handles spell-checking for boolean or ranked queries"""
        if ranked_flag:
            return self.check_spelling_ranked(query, vocab)
        return self.check_spelling_boolean(query, vocab)

    def check_spelling_boolean(self, query, vocab):
        """Checks each term in query for spelling correction, returns new string
           if corrections are made"""
        terms = re.findall("\w+", query)
        new_terms = [term if ('*' in term or remove_special_characters(term) in vocab) else self.select_best_spelling(term) for term in terms]
        if not terms == new_terms:
            if all(new_terms):
                for term, new in zip(terms, new_terms):
                    if term != new:
                        query = query.replace(term, new)
                return query

    def check_spelling_ranked(self, query, vocab):
        """Faster spell check when symbols are not important"""
        terms = query.split()
        new_terms = [term if ('*' in term or remove_special_characters(term) in vocab) else self.select_best_spelling(term) for term in terms]
        if not terms == new_terms:
            if all(new_terms):
                return " ".join(new_terms)

    def select_best_spelling(self, term):
        """Returns the best spelling candidate based on edit distance and document frequency"""
        candidates = self.kgram_index.find_spelling_candidates(term, THRESHOLD)
        if not candidates:
            return None
        frequencies = self.disk_index.get_doc_frequency(candidates)
        return candidates[frequencies.index(max(frequencies))]

    def ranked_query(self, query, k):
        """Returns the k most relevant documents from the corpus for a query,
        using the "term at a time" algorithm"""
        A = defaultdict(int)
        heap = []
        query = [word if '*' in word else query_normalize(word) for word in query.split()]
        for term in query:
            if '*' in term:
                query.extend(self.wildcard_query(term))
                continue
            postings = self.disk_index.get_postings(term)
            if postings:
                wqt = math.log(1 + self.num_docs/len(postings))
                for posting in postings:
                    wdt = 1 + math.log(posting[1])
                    A[posting[0]] += wdt * wqt
        with open('{}docWeights.bin'.format(self.path), 'rb') as f:
            for doc, score in A.items():
                f.seek(8*(doc))
                length = f.read(8)
                ld = struct.unpack('d', length)
                heapq.heappush(heap, (-score/ld[0], doc))
        return [(key, -value) for value, key in heapq.nsmallest(k, heap)]

    def boolean_query(self, query):
        """Returns the documents that satisfy a boolean query using the index"""
        query_literals = self.process_query(query)
        index = self.disk_index.retrieve_postings(query_literals)
        success_doc_ids = []
        for literal in query_literals:
            # Guard for unmatched " symbols
            try:
                queries = shlex.split(literal)
            except ValueError as e:
                print(e)
                print(literal)
                queries = [literal]
            docs_with_all_queries = []
            for subliterals in queries:
                subliterals = subliterals.split()
                wildcard = False
                for term in subliterals:
                    if '*' in term:
                        # Recursively call query to pull new index with wildcard terms, and append the results
                        gram_query = self.wildcard_query(term.lower())
                        gram_query = '+'.join(gram_query)
                        res = self.boolean_query(gram_query)
                        if res:
                            docs_with_all_queries.append(res)
                        wildcard = True
                if wildcard:
                    continue
                subliterals = [query_normalize(term) for term in subliterals]
                combined_postings_lists = list(chain.from_iterable([index[subliteral] for subliteral in subliterals]))
                combined_postings_lists = sorted(combined_postings_lists, key=lambda t:t[0])
                docs_with_current_query = []
                for key,doc_postings in groupby(combined_postings_lists, itemgetter(0)):
                    doc_postings = list(doc_postings)
                    if len(subliterals) > 1:
                        if len(doc_postings) == len(subliterals):
                            subliteral_found = True
                            postings = [x[2] for x in doc_postings]
                            for i in range(len(postings)):
                                postings[i] = [posting - i for posting in postings[i]]
                            results = postings[0]
                            for p in postings[1:]:
                                results = intersect_sorted_lists(results, p)
                            results = list(results)
                            if len(results) > 0:
                                docs_with_current_query.append(doc_postings[0][0])
                    else:
                        docs_with_current_query.append(doc_postings[0][0])
                docs_with_all_queries.append(docs_with_current_query)
            if docs_with_all_queries:
                ids_intersect = docs_with_all_queries[0]
                for l in docs_with_all_queries[1:]:
                    ids_intersect = intersect_sorted_lists(ids_intersect, l)
                success_doc_ids = union_sorted_lists(success_doc_ids, ids_intersect)
        return list(success_doc_ids)

    def wildcard_query(self, query):
        """Puts queries in correct form for the kgram index, splits on grams
        and returns the strings that contain each gram"""
        if not query.startswith('*'):
            query = '$' + query
        if not query.endswith('*'):
            query = query + '$'
        gram_list = query.split('*')
        gram_list = set(filter(None, gram_list))
        return self.kgram_index.get_intersection_grams(gram_list)

    @staticmethod
    def process_query(query):
        """Isolate query literals"""
        literals = query.split('+')
        literals = list(map(str.strip, literals))
        return literals
