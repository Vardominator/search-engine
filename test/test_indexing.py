"""Unit Tests for indexing file"""
import os
import json
import collections
import indexing
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
              "test":    [indexing.PositionalPosting(0,[3]),
                          indexing.PositionalPosting(1,[1]),
                          indexing.PositionalPosting(3,[0, 1, 2, 3, 4]),
                          indexing.PositionalPosting(4,[1])],
              "document":[indexing.PositionalPosting(0,[4]),
                          indexing.PositionalPosting(1,[2]),
                          indexing.PositionalPosting(4,[0])],
              "here":    [indexing.PositionalPosting(1,[4]),
                          indexing.PositionalPosting(2,[0]),
                          indexing.PositionalPosting(4,[3])],
              "we":      [indexing.PositionalPosting(2,[1])],
              "go":      [indexing.PositionalPosting(2,[2])],
              "goe":     [indexing.PositionalPosting(4,[2])],
              "anoth":   [indexing.PositionalPosting(1,[0])],
              "third":   [indexing.PositionalPosting(2,[4])],
              "this":    [indexing.PositionalPosting(0,[0])],
              "is":      [indexing.PositionalPosting(0,[1]),
                          indexing.PositionalPosting(1,[3])],
              "a":       [indexing.PositionalPosting(0,[2]),
                          indexing.PositionalPosting(2,[3])],
              "one":     [indexing.PositionalPosting(2,[5])]
             }
TRUE_INDEX = collections.OrderedDict(sorted(TRUE_INDEX.items(), key=lambda t:t[0]))

with patch("builtins.open", mock_open()) as mock_file:
    index = indexing.create_index(docs)[0]

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
