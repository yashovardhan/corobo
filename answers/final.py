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
                graph.add_node(node, token=token)
            node = graph.node.get(node)
            for key, value in attrs.items():
                node.setdefault(key, []).append(value)
        graph.add_edge(*nodes)

def get_answer(question, graph, final=False):
    q_graph = networkx.Graph()
    q_doc = nlp(question)
    q_type = []
    for token in q_doc:
        if token.tag_.startswith('W'):
            q_type.append(token)

    grapheize(q_graph, q_doc, attrs={'q_type': q_type})
    scores = Counter()
    found_common = False
    for start, end in q_graph.edges():
        found_common = True
        if start in graph and end in graph:
            for path in networkx.algorithms.all_shortest_paths(graph, start, end):
                for node in path:
                    scores.update(graph.node.get(node)['text'])

    sorted_counter = OrderedDict(sorted(scores.items(), key=lambda x: x[1],
                                        reverse=True))
    total_scores = 0
    for i, item in enumerate(sorted_counter.items()):
        if i == 4: break
        total_scores += item[1]

    for i, item in enumerate(sorted_counter.items()):
        scores[item[0]] /= total_scores

    for doc, i in scores.most_common(3):
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
