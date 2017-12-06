import json
import os


def split_nps_json(origin, destination, key, name=''):
    """Splits National Parks JSON into indivdual documents"""
    with open(origin, 'r') as f:
        full_json = json.load(f)
    if not os.path.exists(destination):
        os.makedirs(destination)
    file_num = 1
    for document in full_json[key]:
        with open('{}/{}{}.json'.format(destination, name, file_num), 'w') as j:
            j.write(json.dumps(document))
        file_num += 1


def scripts_to_json(origin, destination='movie_jsons'):
    """Cleans script texts and saves as JSON in desired directory"""
    if not os.path.exists(destination):
        os.makedirs(destination)
    for subdir, dirs, files in os.walk(origin):
        for file in files:
            genre = subdir.split('/')[-1]
            with open('{}/{}'.format(subdir, file), 'r') as f:
                dirty_script = f.read()
                clean = clean_script(dirty_script)
                lines = clean.split('\n')
                title = lines[0]
                script_dict = {'title': title, 'genre': genre, 'body': clean}
                with open('{}/{}.json'.format(destination, file.split('.')[0]), 'w') as j:
                    j.write(json.dumps(script_dict))


def clean_script(text):
    text = text.replace('Back to IMSDb', '')
    text = text.replace(
    '''<b><!--

</b>if (window!= top)

top.location.href=location.href

<b>// -->

</b>''', '')


    text = text.replace('''          Scanned by http://freemoviescripts.com
          Formatting by http://simplyscripts.home.att.net
''', '')
    text = text.replace('<b><!--', '')
    text = text.replace('</b>', '')
    text = text.replace('<b>/*', '')
    text = text.replace('(c) 1990 The Walt Disney Company', '')
    text = text.replace('------------------------------------------------------------', '')
    text = text.replace('<script>', '')
    text = text.replace('for educational use only', '')
    text = text.replace('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-', '')
    return text.replace(r'\r', '').strip()


if __name__ == "__main__":
    scripts_to_json('data/imsdb_movies', 'data/movie_jsons')