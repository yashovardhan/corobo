import docutils
import docutils.nodes
from docutils.parsers.rst import directives
import yaml
import logging
from collections import OrderedDict
import nltk
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS


DATA = {}

def handle_non_section_nodes(section_node, non_section_child_nodes):
    non_code_nodes = filter(lambda x: type(x) not in [docutils.nodes.literal_block],
                            non_section_child_nodes)
    code_nodes = filter(lambda x: type(x) in [docutils.nodes.literal_block],
                        non_section_child_nodes)
    code = '\n'.join(map(lambda x: x.astext(), code_nodes))
    text = '\n'.join(map(lambda x: x.astext(), non_code_nodes))
    DATA[section_node.get('ids')[0]] = {
        "code": code,
        "text": text
    }

class Extractor(docutils.nodes.SparseNodeVisitor):

    def visit_section(self, node):
        non_section_childs = list(filter(lambda x: type(x) != docutils.nodes.section,
                                         node.children))

        handle_non_section_nodes(node, non_section_childs)

def parse_rst(path):
    """
    :param path: The path of the rst file.
    :return: The document object
    """
    rst = open(path)
    default_settings = docutils.frontend.OptionParser(components=(docutils.parsers.rst.Parser, )).get_default_values()
    document = docutils.utils.new_document(rst.name, default_settings)
    parser =  docutils.parsers.rst.Parser()
    parser.parse(rst.read(), document)
    rst.close()
    return document

def extract_info(rst):
    extractor = Extractor(rst)
    rst.walk(extractor)
    global DATA
    return DATA

def parse_index():
    with open('index.yaml') as f:
        index = yaml.load(f)
    for file_name in index.keys():
        try:
            extract_info(parse_rst('coala/docs/Developers/' + file_name))
        except FileNotFoundError:
            logging.warning('File {} was not parsed and collected'.format(file_name))
    global DATA
    for file_name, contents in index.items():
        for section_name, data in contents.items():
            DATA[section_name]['keywords'] = data['keywords']
            DATA[section_name]['answers'] = data['answers']

parse_index()

def answer(question):
    global DATA
    question_tags = list(filter(lambda x: x[1].startswith('W'),
                                nltk.pos_tag(nltk.word_tokenize(question))))
    keyword = set([token for token in simple_preprocess(question) if token not in STOPWORDS])
    docs = OrderedDict(sorted(DATA.items(), key=lambda item: len(keyword.intersection(item[1].get('keywords', []))), reverse=True))
    if question_tags:
        for tag in list(map(lambda x: x[0], question_tags)):
            for section, doc in docs.items():
                if tag in doc['answers']:
                    return '============== code ==============\n' + doc['code'] + '\n\n' + '============== text ==============\n\n' + doc['text']
    else:
        doc = list(docs.items())[0][1]
        return '============== code ==============\n' + doc['code'] + '\n\n' + '============== text ==============\n\n' + doc['text']
    return 'nothing found'
'''
def create_graph():
    index = parse_index()
    for file in index:
        doc = parse_rst('coala/docs/Developers/' + file)
'''

if __name__ == '__main__':
    try:
        while True:
            q = input('>> ')
            print(answer(q))
    except KeyboardInterrupt:
        print('exiting...')