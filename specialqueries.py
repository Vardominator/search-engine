import sys

def special_queries(input):
    if input == 'q':
        sys.exit()
    elif input.startswith('stem '):
        if len(input) > 6:
            print('stemming {}:'.format(input[6:])
        else:
            print('Please provide a term with the stem command.')
            print('e.g., >>>:stem word')
    elif input.startswith('index '):
        if len(input) > 7:
            print('Indexing folder {}:'.format(input[7:]))
        else:
            print('Please provide a directory name with the index command.')
            print('e.g., >>>:index target_folder')
    elif input == 'vocab':
        print('Printing all terms in the vocabulary:')
    else:
        print('Unrecognized command')
