import pickle
import shlex
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

    def build_index(self, index):
        """Calls member methods to write vocab and postings to disk."""
        dictionary = list(index.keys())
        vocab_positions = [None]*len(dictionary)
        self.write_vocab(self.path, dictionary, vocab_positions)
        self.write_postings(self.path, index, dictionary, vocab_positions)

    def write_vocab(self, path, dictionary, vocab_positions):
        """Writes vocab to disk and stores positions in a list."""
        vocab_file = open('{}vocab.bin'.format(path), 'wb')
        vocab_index = 0
        vocab_position = 0
        for term in dictionary:
            vocab_positions[vocab_index] = vocab_position
            vocab_file.write(term.encode())
            vocab_index += 1
            vocab_position += len(term.encode())
        vocab_file.close()

        # # test with reading
        # vocab_file = open('bin/vocab.bin', 'rb')
        # last_position = vocab_positions[0]
        # vocab_words = []
        # for position in vocab_positions[1:]:
        #     vocab_bytes = vocab_file.read(position - last_position)
        #     vocab_words.append(vocab_bytes)
        #     vocab_file.seek(position, 0)
        #     last_position = position

        # print(vocab_words[0:1000])

        # vocab_file = open('bin/vocabtable.bin', 'rb')
        # vocab_position = 0
        # # read first four bytes
        # vocab_size_bytes = vocab_file.read(4)
        # vocab_size_int = int.from_bytes(vocab_size_bytes, byteorder='big')
        # print(vocab_size_int)
        # vocab_file.close()


    def write_postings(self, path, index, dictionary, vocab_positions):
        """Writes postings to disk."""
        vocab_table_file = open('{}vocabtable.bin'.format(path), 'wb')
        postings_file = open('{}postings.bin'.format(path), 'wb')

        # write number of terms in vocab (4 bytes)
        vocab_table_file.write((len(dictionary)).to_bytes(4, byteorder='big'))

        vocab_index = 0
        for term in dictionary:
            postings = index[term]
            # vocab position
            vocab_table_file.write((vocab_positions[vocab_index]).to_bytes(8, byteorder='big'))
            # position in postings file (8 bytes)
            vocab_table_file.write((postings_file.tell()).to_bytes(8, byteorder='big'))
            # number of documents (dft - 4 bytes)
            postings_file.write((len(postings)).to_bytes(4, byteorder='big'))

            last_docid = 0
            for posting in postings:
                postings_list = posting.postings_list
                # doc id as gap (d - 4 bytes)
                postings_file.write((postings_list[0] - last_docid).to_bytes(4, byteorder='big'))
                last_docid = postings_list[0]
                # term frequency (tf_t,d - 4 bytes)
                postings_file.write((len(postings_list[1])).to_bytes(4, byteorder='big'))
                # positions (p1, p2, p3... - 4 bytes)
                for position in postings_list[1]:
                    postings_file.write((position).to_bytes(4, byteorder='big'))

            vocab_index += 1

        vocab_table_file.close()
        postings_file.close()


class DiskIndex(object):
    def __init__(self, path='bin/'):
        self.path = path

    # QUERYING
    # RETURN THREE VALUES PER DOCUMENT IN A TERM'S POSTING LIST: 
    #     1. The document ID
    #     2. The term frequency
    #     3. Positions (optional)

    # ASK NEAL IF YOU CAN USE THE POSITIONS FLAG INSTEAD OF HAVING A SEPARATE METHOD
    def retrieve_postings(self, query):
        """Retrieve postings lists with/without positional information"""
        query_literals = process_query(query)
        vocab_table_file = open('{}vocabtable.bin'.format(self.path), 'rb')
        vocab_file = open('{}vocab.bin'.format(self.path), 'rb')
        postings_file = open('{}postings.bin'.format(self.path), 'rb')

        # TEMPORARY INDEX
        index = {}

        for literal in query_literals:
            all_terms = literal.replace('"', '').split()
            all_terms = [normalize.query_normalize(term) for term in all_terms]
            all_terms = set(all_terms)
            
            positions = False
            if len(all_terms) > 1:
                positions = True

            for subliteral in all_terms:
                # add term to index
                if subliteral not in index:
                    index[subliteral] = []

                    # term count stored in first 4 bytes of file
                    term_count_bytes = vocab_table_file.read(4)
                    term_count = int.from_bytes(term_count_bytes, byteorder='big')

                    # use linear search for now, will user B+ tree later
                    last_position_bytes = vocab_table_file.read(8)
                    last_position = int.from_bytes(last_position_bytes, byteorder='big')

                    for i in range(term_count - 1):
                        # READ POSTING POSITION
                        posting_position_bytes = vocab_table_file.read(8)
                        posting_position = int.from_bytes(posting_position_bytes, byteorder='big')
                        # READ VOCAB POSITION
                        vocab_position_bytes = vocab_table_file.read(8)
                        vocab_position = int.from_bytes(vocab_position_bytes, byteorder='big')
                        # READ WORD AT CURRENT VOCAB POSITION
                        term = vocab_file.read(vocab_position-last_position)
                        last_position = vocab_position
                        # READ NUMBER OF DOCS AT CURRENT POSTING POSITION
                        postings_file.seek(posting_position, 0)
                        number_docs_bytes = postings_file.read(4)
                        number_docs = int.from_bytes(number_docs_bytes, byteorder='big')
                        # FOR EACH DOC READ POSTINGS LIST
                        last_doc_id = 0

                        # only doc id to index if current vocab term
                        if term.decode() == subliteral:
                            for d in range(number_docs):
                                doc_id_gap_bytes = postings_file.read(4)
                                doc_id_gap = int.from_bytes(doc_id_gap_bytes, byteorder='big')
                                # GET DOCID BY ADDING GAP
                                last_doc_id += doc_id_gap
                                # READ TERM FREQUENCY
                                term_freq_bytes = postings_file.read(4)
                                term_freq = int.from_bytes(term_freq_bytes, byteorder='big')
                    
                                current_posting = [last_doc_id, term_freq]
                                
                                # READ TERM POSITIONS
                                if positions:
                                    doc_positions = []
                                    # if positions desired read them
                                    for f in range(term_freq):
                                        position_bytes = postings_file.read(4)
                                        position = int.from_bytes(position_bytes, byteorder='big')
                                        doc_positions.append(position)
                                    current_posting.append(doc_positions)

                                index[subliteral].append(current_posting)

                    vocab_table_file.seek(0)
                    vocab_file.seek(0)
                    postings_file.seek(0)
        
        vocab_table_file.close()
        vocab_file.close()
        postings_file.close()
        return index

    def query_search(self, query, index):
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

                # SPLIT POSTINGS BY DOCUMENT ID
                for key,doc_postings in groupby(combined_postings_lists, itemgetter(0)):
                    doc_postings = list(doc_postings)
                    if len(subliterals) > 1:
                        # CHECK IF LENGTH OF POSTINGS IS THE SAME AS THE SUBLITERALS
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

            # INTERSECT DOC IDs WITH SUCCESSFUL QUERIES
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