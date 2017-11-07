import shlex
import sys
import heapq
import math
import pickle
import struct
from collections import defaultdict
from itertools import chain, groupby
from operator import itemgetter

import normalize
from kgram import KGramIndex
from diskindex import DiskIndex


class QueryProcessor(object):

    def __init__(self, path='bin/'):
        with open('{}kgram.bin'.format(path), 'rb') as f:
            self.kgram_index = pickle.load(f)
        self.ranked_flag = False
        self.disk_index = DiskIndex(path)
        self.k_docs = 10

    def query(self, query):
        index = self.disk_index.retrieve_postings(query)
        if self.ranked_flag:
            return self.ranked_query(query, self.k_docs)
        return self.boolean_query(query, index)

    def set_ranked_flag(self, setting):
        self.ranked_flag = setting

    def ranked_query(self, query, k):
        """Returns the k most relevant documents from the corpus for a query,
        using the "term at a time" algorithm"""
        A = defaultdict(int)
        heap = []
        query = [normalize.query_normalize(word) for word in query.split()]
        for term in query:
            postings = self.disk_index.get_postings(term)
            wqt = math.log(1 + len(postings)/len(postings))
            for posting in postings:
                print(posting)
                wdt = 1 + math.log(posting[1])
                A[posting[0]] += wdt * wqt
        with open('bin/docWeights.bin', 'rb') as f:
            for doc, score in A.items():
                f.seek(8*(doc))
                length = f.read(8)
                print(length)
                ld = struct.unpack('d', length)
                heapq.heappush(heap, (-score/ld[0], doc))
        return [(key, -value) for value, key in heapq.nsmallest(k, heap)]

    def boolean_query(self, query, index):
        query_literals = self.process_query(query)
        success_doc_ids = []
        for literal in query_literals:
            queries = shlex.split(literal)
            docs_with_all_queries = []
            for subliterals in queries:
                if '*' in subliterals:
                    gram_query = self.wildcard_query(subliterals.lower())
                    docs_with_all_queries.append(list(self.query(gram_query)))
                    continue
                subliterals = subliterals.split()
                subliterals = [normalize.query_normalize(term) for term in subliterals]
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
                            results = set.intersection(*map(set, postings))
                            if len(results) > 0:
                                docs_with_current_query.append(doc_postings[0][0])
                    else:
                        docs_with_current_query.append(doc_postings[0][0])
                docs_with_all_queries.append(docs_with_current_query)
            ids_intersect = list(set.intersection(*map(set, docs_with_all_queries)))
            success_doc_ids.extend(ids_intersect)
        # print(success_doc_ids)
        return sorted(set(success_doc_ids))

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
