import shlex
from itertools import chain, groupby
from operator import itemgetter
from specialqueries import special_queries

def process_query(query):
    if query.startswith(':'):
        special_queries(query)
    else:
        literals = query.split('+')
        literals = list(map(str.strip, literals))
        return literals

def query_search(literals, index):
    documents_found = []
    succes_doc_ids = []

    for literal in literals:
        subliterals = shlex.split(literal)

        # COMBINE POSITIONAL POSTING OBJECTS FOR A LITERAL
        combined_postings = list(chain.from_iterable([index[subliteral] for subliteral in subliterals]))

        # EXTRACT POSTINGS LISTS FOR EVERY POSITIONAL POSTING OBJECT
        combined_postings_lists = [posting.postings_list for posting in combined_postings]

        # SORT LISTS BY DOCUMENT ID
        combined_postings_lists = sorted(combined_postings_lists, key=lambda t:t[0])

        # SPLIT POSTINGS BY DOCUMENT ID
        for key,doc_postings in groupby(combined_postings_lists, itemgetter(0)):
            doc_postings = list(doc_postings)

            # CHECK IF LENGTH OF POSTINGS IS THE SAME AS THE SUBLITERALS
            if len(doc_postings) == len(subliterals):
                posting_lists = [posting[1] for posting in doc_postings]
                subliteral_found = True

                for a in range(len(posting_lists) - 1):
                    left_list = posting_lists[a]
                    right_list = posting_lists[a + 1]
                    i = 0
                    j = 0

                    while i < len(left_list) - 1:
                        increment_found = False
                        if left_list[i] < right_list[j] and left_list[i] + 1 != right_list[j]:
                            i += 1
                        elif left_list[i] + 1 == right_list[j]:
                            increment_found = True
                            break
                        else:
                            if j < len(right_list):
                                j += 1

                    if left_list[i] + 1 != right_list[j]:
                        subliteral_found = False
                        break

                if subliteral_found:
                    succes_doc_ids.append(doc_postings[0][0])

    return sorted(set(succes_doc_ids))

if __name__ == "__main__":
    literals = process_query('fourscore and \"Seven Years\"')
    # print(literals)
