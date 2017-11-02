import pickle
import shlex
import sqlite3

from itertools import chain, groupby
from operator import itemgetter
import collections

import normalize
from queryprocessing import process_query
from indexing import PositionalPosting

class IndexWriter(object):
    """Writes inverted index to disk. Terms are extracted from the index.
       The terms are written to disk and the positions of the terms are
       stored in a list. These positions are then used to to write the
       postings to disk."""

    def __init__(self, path='bin/'):
        self.path = path

    def build_index(self, indexes):
        """Calls member methods to write vocab and postings to disk."""
        index = indexes[0]
        kgram_index = indexes[1]
        with open('{}kgram.bin', 'wb') as f:
            pickle.dump(kgram_index, f)
        dictionary = list(index.keys())
        vocab_positions = [None]*len(dictionary)
        self.write_postings(self.path, index, dictionary, vocab_positions)

    def write_postings(self, path, index, dictionary, vocab_positions):
        """Writes postings to disk."""
        postings_file = open('{}postings.bin'.format(path), 'wb')
        conn = sqlite3.connect('bin/vocabtable.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE vocabtable (term TEXT, position INTEGER)''')
        for term in dictionary:
            postings = index[term]
            c.execute("INSERT INTO vocabtable VALUES (?, ?)", (term, postings_file.tell()))
            conn.commit()
            postings_file.write((len(postings)).to_bytes(4, byteorder='big'))
            last_docid = 0
            for posting in postings:
                postings_list = posting.postings_list
                postings_file.write((postings_list[0] - last_docid).to_bytes(4, byteorder='big'))
                last_docid = postings_list[0]
                postings_file.write((len(postings_list[1])).to_bytes(4, byteorder='big'))
                for position in postings_list[1]:
                    postings_file.write((position).to_bytes(4, byteorder='big'))
        conn.close()
        postings_file.close()


class DiskIndex(object):
    """Uses disk index and user query to create in-memory index with terms
       only in the user query. Then processes query and returns relevant documents."""

    def __init__(self, path='bin/'):
        self.path = path

    def retrieve_postings(self, query):
        """Retrieve postings lists with/without positional information"""
        query_literals = process_query(query)
        postings_file = open('{}postings.bin'.format(self.path), 'rb')
        conn = sqlite3.connect('bin/vocabtable.db')
        c = conn.cursor()
        index = {}
        for literal in query_literals:
            all_terms = literal.replace('"', '').split()
            all_terms = [normalize.query_normalize(term) for term in all_terms]
            all_terms = set(all_terms)
            positions = False
            if len(all_terms) > 1:
                positions = True
            for subliteral in all_terms:
                if subliteral not in index:
                    index[subliteral] = []
                    c.execute("SELECT * FROM vocabtable WHERE term=?", (subliteral,))
                    row = c.fetchall()[0]
                    if len(row) > 0:
                        posting_position = row[1]
                        postings_file.seek(posting_position, 0)
                        number_docs_bytes = postings_file.read(4)
                        number_docs = int.from_bytes(number_docs_bytes, byteorder='big')
                        last_doc_id = 0
                        for d in range(number_docs):
                            doc_id_gap_bytes = postings_file.read(4)
                            doc_id_gap = int.from_bytes(doc_id_gap_bytes, byteorder='big')
                            last_doc_id += doc_id_gap
                            term_freq_bytes = postings_file.read(4)
                            term_freq = int.from_bytes(term_freq_bytes, byteorder='big')
                            current_posting = [last_doc_id, term_freq]
                            if positions:
                                doc_positions = []
                                for f in range(term_freq):
                                    position_bytes = postings_file.read(4)
                                    position = int.from_bytes(position_bytes, byteorder='big')
                                    doc_positions.append(position)
                                current_posting.append(doc_positions)
                            index[subliteral].append(current_posting)

        postings_file.close()
        conn.close()
        return index

    def query_search(self, query, index):
        """Query the temporary in-memory index"""
        query_literals = process_query(query)
        success_doc_ids = []
        for literal in query_literals:
            queries = shlex.split(literal)
            docs_with_all_queries = []
            for subliterals in queries:
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
        return sorted(set(success_doc_ids))


if __name__ == "__main__":
    # indexfile = open('bin/indexes', 'rb')
    # indexes = pickle.load(indexfile)
    # index_writer = IndexWriter()
    # index_writer.build_index(indexes[0])
    
    query = '\"a gateway to the wilderness\" + filter'
    disk_index = DiskIndex(path='bin/')
    temp_index = disk_index.retrieve_postings(query)
    query_results = disk_index.query_search(query, temp_index)
    print(len(query_results))
