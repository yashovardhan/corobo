from collections import OrderedDict, Counter
import logging

from gensim.parsing.preprocessing import STOPWORDS
from gensim.utils import simple_preprocess
import networkx
import nltk
import spacy

from answers.extraction import DATA, parse_docs

parse_docs()

nlp = spacy.load('en_core_web_md')

SCORES = {
    "ADJ": 3,
    "NOUN": 3,
    "ADV": 2,
    "VERB": 2,
    "INTJ": 2,
    "X": 2,
    "PRON": 2,
    "ADP": 2,
    "AUX": 1,
    "CONJ": 1,
    "CCONJ": 1,
    "SCONJ": 1,
    "DET": 1,
    "PROPN": 1,
    "PART": 1,
    "": 0,
    "NUM": 0,
    "PUNCT": 0,
    "SYM": 0,
    "EOL": 0,
    "SPACE": 0
}

def grapheize(graph, doc, attrs={}):
    unallowed_tags = [
        'EX', 'HVS', 'MD', 'PDT',
        'IN', 'DT', 'TO', 'CD',
        'CC', '-LRB-', 'HYPH', ':'
    ]
    for token in doc:
        if (token.tag_ in unallowed_tags) or (token == token.head):
            continue
        nodes = [token.lemma_, token.head.lemma_]
        for node in nodes:
            if node not in graph:
                graph.add_node(node, token=Counter())
            node = graph.node.get(node)
            node['token'].update([token.pos_])
            for key, value in attrs.items():
                node.setdefault(key, []).append(value)
        graph.add_edge(*nodes)

def get_answer(question, graph, final=False):
    global SCORES

    q_graph = networkx.Graph()
    q_doc = nlp(question)
    q_type = []
    for token in q_doc:
        if token.tag_.startswith('W'):
            q_type.append(token)

    pos_dict = {a.string.strip(): a.pos_ for a in list(q_doc)}

    grapheize(q_graph, q_doc, attrs={'q_type': q_type})
    scores = Counter()
    found_common = False
    for start, end in q_graph.edges():
        found_common = True
        if start in graph and end in graph:
            for path in networkx.algorithms.all_shortest_paths(graph, start, end):
                for node in path:
                    try:
                        pos = graph.node.get(node)['token'].most_common()[0][0]
                        score = SCORES[pos_dict.get(node, pos)]
                        for text in graph.node.get(node)['text']:
                            scores.update({text: score})
                    except:
                        logging.exception('Something went wrong: ')

    sorted_counter = OrderedDict(sorted(scores.items(), key=lambda x: x[1],
                                        reverse=True))

    items = list(sorted_counter.items())
    min_score = items[-1][1]
    max_score = items[0][1]
    diff_max_min = max_score - min_score

    for item in items:
        key = item[0]
        score = item[1]
        sorted_counter[key] = ((score - min_score) / diff_max_min)

    for doc, i in Counter(sorted_counter).most_common(3):
        yield (doc, i)


def construct_graph():
    graph = networkx.Graph()
    for name, doc in DATA.items():
        meta = {
            'section_name': name,
            'code': doc['code'],
            'text': doc['text']
        }
        grapheize(graph, nlp(doc['text']), meta)
    return graph

graph = construct_graph()

if __name__ == '__main__':
    try:
        mod = lambda y: map(lambda x: (x[0][:100], x[1]), y)
        while True:
            q = input('>> ')
            print(list(mod(list(get_answer(q, graph)))))
    except KeyboardInterrupt:
        print('exiting...')
