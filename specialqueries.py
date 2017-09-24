"""This should be moved over to query processing when finished"""
import sys
from normalize import stem

def special_queries(query):
    if query == 'q':
        sys.exit()
    elif query.startswith('stem '):
        if len(query) > 5:
            word = query[5:]
            print('Stemming word {}:'.format(word))
            print(stem(word))
        else:
            print('Please provide a word with the stem command.')
            print('e.g., >>>:stem word')
    elif query.startswith('index '):
        if len(query) > 6:
            print('Indexing folder {}:'.format(query[6:]))
        else:
            print('Please provide a directory name with the index command.')
            print('e.g., >>>:index target_folder')
    elif input == 'vocab':
        print('Printing all terms in the vocabulary:')
    else:
        print('Unrecognized command')


# Unsure if we need to pass KGramIndex after moving these functions around, but this works for now
def wildcard_query(query, kgram_index):
    if not query.startswith('*'):
        query = '$' + query
    if not query.endswith('*'):
        query = query + '$'
    gram_list = query.split('*')
    gram_list = list(filter(None, gram_list))
    return kgram_index.get_intersection_grams(set(gram_list))
