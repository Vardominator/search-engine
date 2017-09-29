"""Unit Tests for indexing file"""
import os
import json
import collections
import indexing

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

docs = process_documents()

TRUE_INDEX = {
                "test":[indexing.PositionalPosting(1,[3]),
                        indexing.PositionalPosting(2,[1]),
                        indexing.PositionalPosting(4,[0, 1, 2, 3, 4]),
                        indexing.PositionalPosting(5,[1])],
                "document":[indexing.PositionalPosting(1,[4]),
                            indexing.PositionalPosting(2,[2]),
                            indexing.PositionalPosting(5,[0])],
                "here":[indexing.PositionalPosting(2,[4]),
                        indexing.PositionalPosting(3,[0]),
                        indexing.PositionalPosting(5,[3])],
                "we":[indexing.PositionalPosting(3,[1])],
                "go":[indexing.PositionalPosting(3,[2])],
                "goe":[indexing.PositionalPosting(5,[2])],
                "anoth":[indexing.PositionalPosting(2,[0])],
                "third":[indexing.PositionalPosting(3,[4])],
                "this":[indexing.PositionalPosting(1,[0])],
                "is":[indexing.PositionalPosting(1,[1]),
                      indexing.PositionalPosting(2,[3])],
                "a":[indexing.PositionalPosting(1,[2]),
                     indexing.PositionalPosting(3,[3])],
                "one":[indexing.PositionalPosting(3,[5])]
             }
TRUE_INDEX = collections.OrderedDict(sorted(TRUE_INDEX.items(), key=lambda t:t[0]))

index = indexing.create_index(docs)[0]

def test_index_has_all_keys():
    assert(set(index.keys()) == set(TRUE_INDEX.keys()))

def test_index_has_all_postings():
    for word in index.keys():
        assert len(index[word]) == len(TRUE_INDEX[word])