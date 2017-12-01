import heapq
import pickle
import sqlite3
import struct

from normalize import query_normalize
import memoryindex

class IndexWriter(object):
    """Writes inverted index to disk. Terms are extracted from the index.
       The terms are written to disk and the positions of the terms are
       stored in a list. These positions are then used to to write the
       postings to disk."""

    def __init__(self, docs_dir='data/documents', path='bin/'):
        self.docs_dir = docs_dir
        self.path = path
        self.vocab = set()
        self.docids = []

    def build_index(self, processed_docs):
        """Calls member methods to write vocab and postings to disk."""
        indexes = memoryindex.create_index(processed_docs, self.path)
        index = indexes[0]
        kgram_index = indexes[1]
        with open('{}index.bin'.format(self.path), 'wb') as f:
            pickle.dump(index, f)
        with open('{}kgram.bin'.format(self.path), 'wb') as f:
            pickle.dump(kgram_index, f)
        dictionary = list(index.keys())
        vocab_positions = [None]*len(dictionary)
        self.write_postings(index, dictionary, vocab_positions)

    def write_postings(self, index, dictionary, vocab_positions):
        """Writes postings to disk."""
        term_positions = list()
        postings_file = open('{}postings.bin'.format(self.path), 'wb')
        conn = sqlite3.connect('{}vocabtable.db'.format(self.path))
        c = conn.cursor()
        c.execute('''DROP TABLE if exists vocabtable''')
        conn.commit()
        c.execute('''CREATE TABLE vocabtable (term TEXT, position INTEGER)''')
        for term in dictionary:
            postings = index[term]
            term_positions.append((term, postings_file.tell()))
            postings_file.write((len(postings)).to_bytes(4, byteorder='big'))
            last_docid = 0
            for posting in postings:
                postings_list = posting.postings_list
                postings_file.write((postings_list[0] - last_docid).to_bytes(4, byteorder='big'))
                last_docid = postings_list[0]
                postings_file.write((len(postings_list[1])).to_bytes(4, byteorder='big'))
                for position in postings_list[1]:
                    postings_file.write((position).to_bytes(4, byteorder='big'))
        c.executemany("INSERT INTO vocabtable VALUES (?, ?)",term_positions)
        conn.commit()
        conn.close()
        postings_file.close()


class DiskIndex(object):
    """Uses disk index and user query to create in-memory index with terms
       only in the user query. Then processes query and returns relevant documents."""

    def __init__(self, path='bin/'):
        self.path = path

    def get_doc_frequency(self, terms):
        """Returns the document frequency of a sequence of terms"""
        postings_file = open('{}postings.bin'.format(self.path), 'rb')
        conn = sqlite3.connect('{}vocabtable.db'.format(self.path))
        c = conn.cursor()
        frequencies = list()
        for term in terms:
            term = query_normalize(term)
            c.execute("SELECT * FROM vocabtable WHERE term=?",(term,))
            row = c.fetchone()
            number_docs = 0
            if row:
                posting_position = row[1]
                postings_file.seek(posting_position, 0)
                number_docs_bytes = postings_file.read(4)
                number_docs = int.from_bytes(number_docs_bytes, byteorder='big')
            frequencies.append(number_docs)
        c.close()
        conn.close()
        postings_file.close()
        return frequencies

    def get_postings(self, term, positions=False):
        """Returns postings for a single term in the index, with or
           without positional information"""
        postings_file = open('{}postings.bin'.format(self.path), 'rb')
        conn = sqlite3.connect('{}vocabtable.db'.format(self.path))
        c = conn.cursor()
        term = query_normalize(term)
        postings = list()
        c.execute("SELECT * FROM vocabtable WHERE term=?",(term,))
        for row in c:
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
                else:
                    postings_file.seek(term_freq*4, 1)
                postings.append(current_posting)
        c.close()
        conn.close()
        postings_file.close()
        return postings

    def retrieve_postings(self, query_literals):
        """Retrieve postings lists with/without positional information"""
        positions = False
        if any('\"' in lit for lit in query_literals):
            positions = True
        postings_file = open('{}postings.bin'.format(self.path), 'rb')
        conn = sqlite3.connect('{}vocabtable.db'.format(self.path))
        c = conn.cursor()
        index = {}
        for literal in query_literals:
            all_terms = literal.split()
            all_terms = [query_normalize(term) for term in all_terms]
            all_terms = set(all_terms)
            for subliteral in all_terms:
                if subliteral not in index:
                    index[subliteral] = []
                    c.execute("SELECT * FROM vocabtable WHERE term=?", (subliteral,))
                    for row in c:
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
                            else:
                                postings_file.seek(term_freq*4, 1)
                            index[subliteral].append(current_posting)

        postings_file.close()
        conn.close()
        return index

    def get_vocab(self):
        conn = sqlite3.connect('{}vocabtable.db'.format(self.path))
        conn.row_factory = lambda cursor, row: row[0]
        c = conn.cursor()
        vocab = c.execute('SELECT term FROM vocabtable').fetchall()
        conn.close()
        return vocab

    @staticmethod
    def get_k_scores(docs, k, path):
        heap = []
        with open('{}docWeights.bin'.format(path), 'rb') as f:
            for doc, score in docs.items():
                f.seek(8*(doc))
                length = f.read(8)
                ld = struct.unpack('d', length)
                heapq.heappush(heap, (-score/ld[0], doc))
        return [(key, -value) for value, key in heapq.nsmallest(k, heap)]
