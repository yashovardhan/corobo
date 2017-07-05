"""
Handles the parsing and extraction of information from rST doc files.
"""

import os

import docutils
import docutils.nodes
import docutils.parsers.rst

# This is the variable in which all of the documentation will be parsed and
# stored.
# Documentation of section x-y-z is stored in DATA['x-y-z']
DATA = {}


class Extractor(docutils.nodes.SparseNodeVisitor):
    """
    Node visitor to extract information from nodes.
    """

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

def handle_non_section_nodes(section_node, non_section_child_nodes):
    """
    All the ndoes that are not section nodes are parsed here.
    """
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

def get_abs_path(path):
    """
    Returns absolute path for paths wrt to this module.
    """
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), path)

def parse_docs():
    """
    Parse all documentation files and store information in DATA
    """
    global DATA
    for files in os.listdir(get_abs_path('coala/docs/Developers')):
        rst = parse_rst(get_abs_path('coala/docs/Developers/' + files))
        extractor = Extractor(rst)
        rst.walk(extractor)
