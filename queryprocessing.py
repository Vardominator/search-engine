import shlex

def process_query(query):
    literals = query.split('+')
    literals = list(map(str.strip, literals))
    return literals

def query_search(literals, index):
    documents_found = []
    for literal in literals:
        if literal in index:
            postings = index[literal]
            for posting in postings:
                documents_found.append(posting.postings_list[0])
                # print(posting.postings_list)
        else:
            print("invalid literal")

    return documents_found

if __name__ == "__main__":
    literals = process_query('bla1   + blah2 + smoothies mango + "Jamba Juice"')
    print(literals)