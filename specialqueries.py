import sys

def special_queries(query):
    if query == 'q':
        sys.exit()
    elif query.startswith('stem '):
        if len(query) > 5:
            print('Stemming word {}:'.format(query[5:]))
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
