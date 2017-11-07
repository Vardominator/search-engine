"""Unit Tests for memoryindex file"""
import os
import json
import collections
import memoryindex
from unittest.mock import patch, mock_open

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
              "test":    [memoryindex.PositionalPosting(0,[3]),
                          memoryindex.PositionalPosting(1,[1]),
                          memoryindex.PositionalPosting(3,[0, 1, 2, 3, 4]),
                          memoryindex.PositionalPosting(4,[1])],
              "document":[memoryindex.PositionalPosting(0,[4]),
                          memoryindex.PositionalPosting(1,[2]),
                          memoryindex.PositionalPosting(4,[0])],
              "here":    [memoryindex.PositionalPosting(1,[4]),
                          memoryindex.PositionalPosting(2,[0]),
                          memoryindex.PositionalPosting(4,[3])],
              "we":      [memoryindex.PositionalPosting(2,[1])],
              "go":      [memoryindex.PositionalPosting(2,[2])],
              "goe":     [memoryindex.PositionalPosting(4,[2])],
              "anoth":   [memoryindex.PositionalPosting(1,[0])],
              "third":   [memoryindex.PositionalPosting(2,[4])],
              "this":    [memoryindex.PositionalPosting(0,[0])],
              "is":      [memoryindex.PositionalPosting(0,[1]),
                          memoryindex.PositionalPosting(1,[3])],
              "a":       [memoryindex.PositionalPosting(0,[2]),
                          memoryindex.PositionalPosting(2,[3])],
              "one":     [memoryindex.PositionalPosting(2,[5])]
             }
TRUE_INDEX = collections.OrderedDict(sorted(TRUE_INDEX.items(), key=lambda t:t[0]))

with patch("builtins.open", mock_open()) as mock_file:
    index = memoryindex.create_index(docs)[0]

def test_index_has_all_keys():
    """Checks to make sure the index has the right number of keys"""
    assert(set(index.keys()) == set(TRUE_INDEX.keys()))

def test_index_has_all_postings():
    """Checks each word in the index to see if it has the right
       number of documents"""
    for word in index.keys():
        assert len(index[word]) == len(TRUE_INDEX[word])

def test_index_collects_all_positions_in_document():
    """Checks to make sure the index captures all positions for a
       term appearing multiple times"""
    assert index['test'][2].postings_list == (3, [0, 1, 2, 3, 4])
