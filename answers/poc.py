import docutils
import nltk
from docutils.parsers.rst import directives
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS

class NLPNode(docutils.nodes.comment):
    """
    This is a node to capture metadata, it does not affect the resulting HTML
    whatsover.
    """
    pass

class NLPDirective(docutils.parsers.rst.Directive):

    required_arguments = 0
    optional_arguments = 0
    has_content = True
    option_spec = {
        'question_type': directives.unchanged,
        'keywords': directives.unchanged
    }

    def run(self):
        question_type = self.options['question_type'].strip().replace(',', ' ').split()
        keywords = self.options['keywords'].strip().replace(',', ' ').split()
        node = NLPNode(question_type=question_type, keywords=keywords)
        return [node]

docutils.parsers.rst.directives.register_directive('nlp', NLPDirective)

DATA = []

def handle_visit(node):
    data = dict()
    data['keywords'] = node.get('keywords')
    data['question_type'] = node.get('question_type')
    section = node.next_node(# condition=lambda x: isinstance(x, docutils.nodes.section),
                             siblings=True)
    data['section'] = section.astext() if section else ''
    DATA.append(data)

class NLPNodeVisitor(docutils.nodes.SparseNodeVisitor):
    def visit_NLPNode(self, node):
        handle_visit(node)

    def depart_NLPNode(self, node):
        pass

def parse_rst(path):
    rst = open(path)
    default_settings = docutils.frontend.OptionParser(components=(docutils.parsers.rst.Parser, )).get_default_values()
    document = docutils.utils.new_document(rst.name, default_settings)
    parser =  docutils.parsers.rst.Parser()
    parser.parse(rst.read(), document)
    rst.close()
    return document

def extract_info(document):
    visitor = NLPNodeVisitor(document)
    document.walk(visitor)

extract_info(parse_rst('branch.rst'))

def answer(question):
    question_tags = list(filter(lambda x: x[1].startswith('W'),
                                 nltk.pos_tag(nltk.word_tokenize(question))))
    keyword = [token for token in simple_preprocess(question) if token not in STOPWORDS][0]
    docs = filter(lambda x: keyword in x['keywords'],
                  DATA)
    if question_tags:
        for doc in docs:
            for tag in list(map(lambda x: x[0], question_tags)):
                if tag in doc['question_type']:
                    return doc['section']
        return 'Dunno :('
    else:
        return 'Doesn\'t look like a question to me :/'



if __name__ == '__main__':
    while True:
        question = input('>>>')
        print(answer(question))



