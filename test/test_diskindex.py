import os
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

def test_index_creation():
    iw = diskindex.IndexWriter(docs_dir='test/test_docs',path='test/bin/')
    iw.build_index(TEST_DOCS)
    assert os.path.isfile('test/bin/postings.bin')

def test_all_files_exist():
    path = 'test/bin/'
    assert os.path.isfile('{}index.bin'.format(path)) and
           os.path.isfile('{}kgram.bin'.format(path)) and
           os.path.isfile('{}vocabtable.db'.format(path))
