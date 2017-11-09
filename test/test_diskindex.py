import json
import os
import sqlite3
import diskindex

def process_documents():
    """Helper function to pre-process documents"""
    docs = []
    docs_dir = 'test/test_docs'

    for root,dirs,files in os.walk(docs_dir):
        files = sorted(files)

        for file in files:
            with open(os.path.join(docs_dir, file), 'r') as json_data:
                content = json.load(json_data)
                docs.append(content['body'])
    return docs

TEST_DOCS = process_documents()
PATH = 'test/bin/'

if not os.path.exists('test/bin'):
    os.mkdir('test/bin')

def test_index_creation():
    """Checking postings file is created when ran"""
    iw = diskindex.IndexWriter(docs_dir='test/test_docs',path=PATH)
    iw.build_index(TEST_DOCS)
    assert os.path.isfile('{}postings.bin'.format(PATH))

def test_all_files_exist():
    """Checking all expected files have been created"""
    assert (os.path.isfile('{}index.bin'.format(PATH)) and
            os.path.isfile('{}kgram.bin'.format(PATH)) and
            os.path.isfile('{}vocabtable.db'.format(PATH)))

def test_vocabtable_init():
    """Checking that all terms are stored in db"""
    with sqlite3.connect('{}vocabtable.db'.format(PATH)) as conn:
        c = conn.cursor()
        c.execute("""SELECT COUNT (*) FROM vocabtable""")
        r = c.fetchone()
        assert r[0] == 12

def test_postings_mapped():
    """Checking seek position points to valid doc frequency numbers"""
    with sqlite3.connect('{}vocabtable.db'.format(PATH)) as conn:
        c = conn.cursor()
        c.execute("""SELECT * FROM vocabtable""")
        r = c.fetchall()
        with open("{}postings.bin".format(PATH), 'rb') as f:
            for row in r:
                f.seek(row[1])
                number_docs_bytes = f.read(4)
                number_docs = int.from_bytes(number_docs_bytes, byteorder='big')
                assert abs(number_docs) < 6

def test_number_docs_correct():
    """Checking for each doc that doc frequencies and term frequencies map
       to valid values in file"""
    with sqlite3.connect('{}vocabtable.db'.format(PATH)) as conn:
        c = conn.cursor()
        c.execute("""SELECT * FROM vocabtable""")
        r = c.fetchall()
        with open("{}postings.bin".format(PATH), 'rb') as f:
            for row in r:
                f.seek(row[1])
                number_docs_bytes = f.read(4)
                number_docs = int.from_bytes(number_docs_bytes, byteorder='big')
                for doc in range(number_docs):
                    doc_id_gap_bytes = f.read(4)
                    doc_id_gap = int.from_bytes(doc_id_gap_bytes, byteorder='big')
                    term_freq_bytes = f.read(4)
                    term_freq = int.from_bytes(term_freq_bytes, byteorder='big')
                    pos_list = []
                    for freq in range(term_freq):
                        position_bytes = f.read(4)
                        position = int.from_bytes(position_bytes, byteorder='big')
                        pos_list.append(position)
                    assert (doc_id_gap >= 0 and term_freq > 0 and len(pos_list) == term_freq)

def test_single_term():
    """Checking that each value for an expected term is correct in file"""
    expected_term = 'a'
    doc_term_frequency = [2, 1]
    with sqlite3.connect('{}vocabtable.db'.format(PATH)) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM vocabtable WHERE term=?",(expected_term,))
        row = c.fetchone()
        with open("{}postings.bin".format(PATH), 'rb') as f:
            # Sanity check
            assert row[0] == expected_term
            f.seek(row[1])
            number_docs_bytes = f.read(4)
            number_docs = int.from_bytes(number_docs_bytes, byteorder='big')
            # Should only be in two documents
            assert number_docs == doc_term_frequency[0]
            for doc in range(number_docs):
                doc_id_gap_bytes = f.read(4)
                doc_id_gap = int.from_bytes(doc_id_gap_bytes, byteorder='big')
                term_freq_bytes = f.read(4)
                term_freq = int.from_bytes(term_freq_bytes, byteorder='big')
                pos_list = []
                for freq in range(term_freq):
                    position_bytes = f.read(4)
                    position = int.from_bytes(position_bytes, byteorder='big')
                    pos_list.append(position)
                # Should only show up in each document once
                assert term_freq == doc_term_frequency[1]

def test_get_postings_one_term_no_positions():
    """Checking correct values returned for a single term from file without positions"""
    term = "one"
    disk_index = diskindex.DiskIndex(path=PATH)
    assert disk_index.get_postings(term) == [[2, 1]]

def test_get_postings_one_term_with_positions():
    """Checking correct values returned for a single term from file with positions"""
    term = "one"
    disk_index = diskindex.DiskIndex(path=PATH)
    assert disk_index.get_postings(term, positions=True) == [[2, 1, [5]]]

def test_retrieve_postings_query():
    """Checking correct values returned for a query from file without positions"""
    query = ["a one"]
    disk_index = diskindex.DiskIndex(path=PATH)
    assert disk_index.retrieve_postings(query) == {"a":[[0, 1], [2, 1]], "one":[[2, 1]]}

def test_retrieve_postings_positional_query():
    """Checking correct values returned for a query from file with positions"""
    query = ['\"a one\"']
    disk_index = diskindex.DiskIndex(path=PATH)
    assert disk_index.retrieve_postings(query) == {"a":[[0, 1, [2]], [2, 1, [3]]], "one":[[2, 1, [5]]]}

def test_vocab_retrieval():
    """Checking whole vocab is retrieved correctly"""
    VOCAB = {'test', 'document', 'here', 'we', 'go', 'goe', 'anoth',
             'third', 'this', 'is', 'a', 'one'}
    disk_index = diskindex.DiskIndex(path=PATH)
    assert set(disk_index.get_vocab()) == VOCAB
