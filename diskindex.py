import heapq
import re
import sqlite3
import struct

import json
import os
from collections import OrderedDict, defaultdict
from glob import glob
from math import sqrt, log
from normalize import query_normalize, normalize, remove_special_characters
from memoryindex import PositionalPosting
from utils import result_iter

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
            c.execute("SELECT * FROM vocabtable WHERE term=?", (term,))
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
        c.execute("SELECT * FROM vocabtable WHERE term=?", (term,))
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
        """Returns the top k scores after dividing each by the document length"""
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
        """Returns the postings at a given position in file, positional
           information is optional"""
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
        print("Building...")
        if not os.path.exists(self.destination):
            os.makedirs(self.destination)

        conn = sqlite3.connect('{}/temp.db'.format(self.destination))
        c = conn.cursor()
        c.execute('DROP TABLE if exists vocab')
        c.execute('CREATE TABLE vocab (term TEXT PRIMARY KEY)')
        c.execute('DROP TABLE if exists block')
        c.execute('CREATE TABLE block (block_id INTEGER PRIMARY KEY)')
        c.execute('DROP TABLE if exists vocab_block')
        c.execute('''CREATE TABLE vocab_block (position INTEGER, term TEXT, block_id INTEGER,
                                              FOREIGN KEY(term) REFERENCES vocab(term),
                                              FOREIGN KEY(block_id) REFERENCES block(block_id))''')
        conn.commit()
        doc_weights = open('{}/docWeights.bin'.format(self.destination), 'wb')
        block_count = 0
        dictionary = OrderedDict()
        vocab_table_terms = []
        # size in bites for number of documents
        size = 4
        for subdir, dirs, files in os.walk(self.origin):
            files = sorted(files)
            for file in files:
                term_map = defaultdict(int)
                with open('{}/{}'.format(subdir, file), 'r') as f:
                    json_object = json.load(f)
                    preterms = json_object['body'].split()
                    position = 0
                    for word in preterms:
                        word = remove_special_characters(word)
                        terms = normalize(word)
                        for term in terms:
                            term_map[term] += 1
                            vocab_table_terms.append((term,))
                            if term not in dictionary:
                                dictionary[term] = []
                            if not dictionary[term]:
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
                if size > self.blocksize:
                    c.execute("INSERT INTO block VALUES (?)", (block_count,))
                    c.executemany("INSERT OR IGNORE INTO vocab (term) VALUES (?)", vocab_table_terms)
                    self.write_block_to_disk(dictionary, block_count, c)
                    conn.commit()
                    block_count += 1
                    dictionary.clear()
                    vocab_table_terms.clear()
                    size = 0

            # if size <= self.blocksize:
            c.execute("INSERT INTO block VALUES (?)", (block_count, ))
            c.executemany("INSERT OR IGNORE INTO vocab (term) VALUES (?)", vocab_table_terms)
            self.write_block_to_disk(dictionary, block_count, c)

        doc_weights.close()
        c.execute('CREATE INDEX index_vocab_block ON vocab_block (term)')
        conn.commit()
        self.merge(c)
        conn.commit()
        conn.close()
        os.remove('{}/temp.db'.format(self.destination))

    def write_block_to_disk(self, dictionary, block_count, dbcursor):
        with open('{}/block{}.bin'.format(self.destination, block_count), 'wb') as block_output:
            term_positions = []
            for term in dictionary.keys():
                postings = dictionary[term]
                term_positions.append((block_output.tell(), term, block_count))
                self.write_postings(block_output, postings)
            dbcursor.executemany("INSERT INTO vocab_block VALUES (?, ?, ?)", term_positions)

    def merge(self, dbcursor):
        """Merges blocks created by SPIMI algorithm. Opens all block files, and creates a new database
           for the final vocab table. Each term's postings are combined and written to a final index
           file. All blocks are deleted on successful merge."""
        print("Merging...")
        term_positions = []
        block_list = []
        outconn = sqlite3.connect('{}/vocabtable.db'.format(self.destination))
        out_cur = outconn.cursor()
        out_cur.execute('DROP TABLE if exists vocabtable')
        out_cur.execute('CREATE TABLE vocabtable (term TEXT PRIMARY KEY, position INTEGER)')
        for name in sorted(glob("{}/block*".format(self.destination)), key=lambda x: int(re.split(r'(/+|\\+)', x)[-1][5:-4])):
            block_list.append(open(name, 'rb'))
        postings_file = open('{}/postings.bin'.format(self.destination), 'wb')
        dbcursor.execute("SELECT DISTINCT term FROM vocab ORDER BY term")
        # Using generator and getting 10000 results at a time, second cursor so place is maintained
        conn2 = sqlite3.connect('{}/temp.db'.format(self.destination))
        inner_cursor = conn2.cursor()
        for term in result_iter(dbcursor):
            term = term[0]
            inner_cursor.execute("SELECT block_id, position FROM vocab_block WHERE term = ?", (term,))
            blocks = inner_cursor.fetchall()
            postings = []
            for block in blocks:
                block_postings = self.get_block_postings(block_list[block[0]], block[1])
                postings.extend(block_postings)
            position = self.write_postings(postings_file, postings)
            term_positions.append((term, position))
            if len(term_positions) > 10000:
                out_cur.executemany("INSERT INTO vocabtable VALUES (?, ?)", term_positions)
                outconn.commit()
                term_positions.clear()
        inner_cursor.close()
        conn2.close()
        if term_positions:
            out_cur.executemany("INSERT INTO vocabtable VALUES (?, ?)", term_positions)
            outconn.commit()
        outconn.close()
        for block in block_list:
            block.close()
            os.remove(block.name)
        postings_file.close()

    @staticmethod
    def write_postings(postings_file, postings):
        """Writes postings to a given file and returns the seek position."""
        start_position = postings_file.tell()
        postings_file.write((len(postings)).to_bytes(4, byteorder='big'))
        last_doc_id = 0
        for posting in postings:
            postings_list = posting.postings_list
            try:
                postings_file.write((postings_list[0] - last_doc_id).to_bytes(4, byteorder='big'))
            except Exception:
                print('docID:{}, last_doc_id:{}'.format(postings_list[0], last_doc_id))
                raise
            postings_file.write(len(postings_list[1]).to_bytes(4, byteorder='big'))
            last_doc_id = postings_list[0]
            for position in postings_list[1]:
                postings_file.write((position).to_bytes(4, byteorder='big'))
        return start_position

    @staticmethod
    def get_block_postings(block, position):
        """Retrieves the positional postings from a file at a specified position."""
        block.seek(position)
        number_docs_bytes = block.read(4)
        number_docs = int.from_bytes(number_docs_bytes, byteorder='big')
        block_postings = []
        last_doc_id = 0
        for d in range(number_docs):
            doc_id_gap_bytes = block.read(4)
            doc_id_gap = int.from_bytes(doc_id_gap_bytes, byteorder='big')
            last_doc_id += doc_id_gap
            block_postings.append(PositionalPosting(last_doc_id, []))
            term_freq_bytes = block.read(4)
            term_freq = int.from_bytes(term_freq_bytes, byteorder='big')
            for f in range(term_freq):
                position_bytes = block.read(4)
                position = int.from_bytes(position_bytes, byteorder='big')
                block_postings[-1].add_position(position)
        return block_postings

    @staticmethod
    def pack_weight(term_map):
        """Calculates the document weight and packs it into an 8 byte double."""
        weight = sqrt(sum([(1 + log(val))**2 for val in term_map.values()]))
        return struct.pack("d", weight)

if __name__ == "__main__":
    spimi = Spimi(1000, origin='data/test_script_jsons', destination='data/test_spimi_blocks')
