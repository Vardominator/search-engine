import heapq
import pickle
import sqlite3
import struct

import sys
import json
import os
from collections import OrderedDict, defaultdict
from glob import glob
from math import sqrt, log
from operator import itemgetter
from normalize import query_normalize
import memoryindex
from memoryindex import PositionalPosting

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
            postings = self.get_current_posting(postings_file, row[1], positions)
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
                        index[subliteral] = self.get_current_posting(postings_file, row[1], positions)
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

    def get_k_scores(self, docs, k):
        heap = []
        with open('{}docWeights.bin'.format(self.path), 'rb') as f:
            for doc, score in docs.items():
                f.seek(8*(doc))
                length = f.read(8)
                ld = struct.unpack('d', length)
                heapq.heappush(heap, (-score/ld[0], doc))
        return [(key, -value) for value, key in heapq.nsmallest(k, heap)]

    @staticmethod
    def get_current_posting(postings_file, posting_position, positions):
        postings = []
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
        return postings


class Spimi():
    def __init__(self, blocksize=1000000000, origin='', destination=''):
        self.blocksize = blocksize
        self.origin = origin
        self.destination = destination
        self.index = self.build()

    def build(self):
        if not os.path.exists(self.destination):
            os.makedirs(self.destination)

        conn = sqlite3.connect('{}/vocabtable.db'.format(self.destination))
        c = conn.cursor()
        c.execute('DROP TABLE if exists vocab')
        c.execute('CREATE TABLE vocab (termID INTEGER PRIMARY KEY, term TEXT)')
        c.execute('DROP TABLE if exists block')
        c.execute('CREATE TABLE block (block_id INTEGER PRIMARY KEY)')
        c.execute('DROP TABLE if exists vocab_block')
        c.execute('''CREATE TABLE vocab_block (position INTEGER, term TEXT, block_id INTEGER,
                                              FOREIGN KEY(term) REFERENCES vocab(term),
                                              FOREIGN KEY(block_id) REFERENCES block(block_id))''')
        c.execute('DROP TABLE if exists sorted_vocab')
        c.execute('CREATE TABLE sorted_vocab (id INTEGER PRIMARY KEY, term TEXT)')

        conn.commit()
        doc_weights = open('{}/docWeights.bin'.format(self.destination), 'wb')
        term_map = defaultdict(int)
        block_count = 0
        dictionary = OrderedDict()
        vocab_table_terms = []
        # size in bites for number of documents
        size = 4
        for subdir, dirs, files in os.walk(self.origin):
            for file in sorted(files):
                with open('{}/{}'.format(subdir, file), 'r') as script_file:
                    script = json.load(script_file)
                    terms = [query_normalize(term) for term in script['body'].split()]
                    position = 0
                    for term in terms:
                        term_map[term] += 1
                        vocab_table_terms.append((term,))
                        if size > self.blocksize and terms.index(term) == len(terms) - 1:
                            c.execute("INSERT INTO block VALUES (?)", (block_count,))
                            c.executemany("INSERT OR IGNORE INTO vocab (term) VALUES (?)", vocab_table_terms)
                            self.write_block_to_disk(dictionary, block_count, c)
                            conn.commit()
                            block_count += 1
                            del dictionary
                            dictionary = {}
                            del vocab_table_terms
                            vocab_table_terms = []
                            size = 0
                        if term not in dictionary:
                            dictionary[term] = []
                        if len(dictionary[term]) == 0:
                            dictionary[term].append(PositionalPosting(files.index(file), [position]))
                        else:
                            last_posting = dictionary[term][-1]
                            if last_posting.postings_list[0] == files.index(file):
                                last_posting.add_position(position)
                            else:
                                dictionary[term].append(PositionalPosting(files.index(file), [position]))
                            size += 4
                        size += 4
                        position += 1
                doc_weights.write(self.pack_weight(term_map))

            if size <= self.blocksize:
                c.execute("INSERT INTO block VALUES (?)", (block_count, ))
                c.executemany("INSERT OR IGNORE INTO vocab (term) VALUES (?)", vocab_table_terms)
                self.write_block_to_disk(dictionary, block_count, c)

        doc_weights.close()
        c.execute('INSERT INTO sorted_vocab (term) SELECT DISTINCT term FROM vocab ORDER BY term')
        conn.commit()
        self.merge(c)
        conn.commit()
        conn.close()

    def write_block_to_disk(self, dictionary, block_count, dbcursor):
        with open('{}/block{}.bin'.format(self.destination, block_count), 'wb') as block_output:
            term_positions = []
            for term in dictionary.keys():
                postings = dictionary[term]
                term_positions.append((block_output.tell(), term, block_count))
                self.write_postings(block_output, postings)
            dbcursor.executemany("INSERT INTO vocab_block VALUES (?, ?, ?)", term_positions)

    def merge(self, dbcursor):
        dbcursor.execute('DROP TABLE if exists vocabtable')
        dbcursor.execute('CREATE TABLE vocabtable (term TEXT PRIMARY KEY, position INTEGER)')
        term_positions = []
        block_list = []
        for name in sorted(glob("{}/block*".format(self.destination))):
            block_list.append(open(name, 'rb'))
        dbcursor.execute("SELECT count(*) FROM sorted_vocab")
        num_terms = dbcursor.fetchone()[0]
        postings_file = open('{}/postings.bin'.format(self.destination), 'wb')
        for i in range(1,num_terms + 1):
            dbcursor.execute("SELECT term FROM sorted_vocab WHERE id = ?", (i,))
            term = dbcursor.fetchone()[0]
            dbcursor.execute("SELECT block_id, position FROM vocab_block WHERE term = ?",(term,))
            blocks = dbcursor.fetchall()
            postings = []
            for block in blocks:
                block_postings = self.get_block_postings(block_list[block[0]], block[1])
                postings.extend(block_postings)
            position = self.write_postings(postings_file, postings)
            term_positions.append((term, position))
        dbcursor.executemany("INSERT INTO vocabtable VALUES (?, ?)",term_positions)
        for f in block_list:
            f.close()
            os.remove(f.name)
        postings_file.close()

    @staticmethod
    def write_postings(postings_file, postings):
        start_position = postings_file.tell()
        postings_file.write((len(postings)).to_bytes(4, byteorder='big'))
        for posting in postings:
            postings_list = posting.postings_list
            postings_file.write((postings_list[0]).to_bytes(4, byteorder='big'))
            postings_file.write(len(postings_list[1]).to_bytes(4, byteorder='big'))
            for position in postings_list[1]:
                postings_file.write((position).to_bytes(4, byteorder='big'))
        return start_position

    @staticmethod
    def get_block_postings(block, position):
        block.seek(position)
        number_docs_bytes = block.read(4)
        number_docs = int.from_bytes(number_docs_bytes, byteorder='big')
        block_postings = []
        for d in range(number_docs):
            doc_id_bytes = block.read(4)
            doc_id = int.from_bytes(doc_id_bytes, byteorder='big')
            block_postings.append(PositionalPosting(doc_id, []))
            term_freq_bytes = block.read(4)
            term_freq = int.from_bytes(term_freq_bytes, byteorder='big')
            for f in range(term_freq):
                position_bytes = block.read(4)
                position = int.from_bytes(position_bytes, byteorder='big')
                block_postings[-1].add_position(position)
        return block_postings

    @staticmethod
    def pack_weight(term_map):
        return struct.pack("d", sqrt(sum([(1 + log(val))**2 for val in term_map.values()])))

if __name__ == "__main__":
    spimi = Spimi(1024, 'test/test_docs', 'data/test_spimi_blocks')
