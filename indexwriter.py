import pickle

class DiskPositionalIndex(object):
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

        # print(vocab_words[0:10])

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
            # write vocab entry for term: byte location of the term in the vocab list and
            # the byte location of the postings for the term in the postings file
            vocab_table_file.write((vocab_positions[vocab_index]).to_bytes(8, byteorder='big'))
            vocab_table_file.write((postings_file.tell()).to_bytes(8, byteorder='big'))
            # write the postings file for term: document frequency for term then the doc ids, encoded as gaps
            postings_file.write((len(postings)).to_bytes(4, byteorder='big'))

            last_docid = 0
            for posting in postings:
                postings_list = posting.postings_list
                postings_file.write((postings_list[0] - last_docid).to_bytes(4, byteorder='big'))
                last_docid = postings_list[0]

            vocab_index += 1

        vocab_table_file.close()
        postings_file.close()


if __name__ == "__main__":
    indexfile = open('bin/indexes', 'rb')
    indexes = pickle.load(indexfile)

    diskindex = DiskPositionalIndex()
    diskindex.build_index(indexes[0])
