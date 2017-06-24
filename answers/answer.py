import yaml

from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS

def pre_process(text: str):
    """
    Return list of tokens after processing the text.
    :param text: The text that has to be processed.
    :return: A list of tokens.
    """
    return [token for token in simple_preprocess(text) if token not in STOPWORDS]

def get_keyword(text: str):
    """
    Given a text find the keyword of text
    """
    raise NotImplementedError

def collect_data():
    """
    Collect all the data yaml files and return a dict of files with keys as file
    name and values as loaded yaml files
    """
    raise NotImplementedError

def all_keywords():
    """
    Read the keyword key from all the yaml files and return a set of keywords
    :return: A set of keywords
    """
    raise NotImplementedError

def expected_ans(question: str):
    """
    Return whether a question expects a what, why, when, command, etc.
    """
    raise NotImplementedError

def rate_answers(question: str, answers: list):
    """
    Returns a list of tuples ('answer', confidence: int) sorted descendingly
    with confidence.
    """
    raise NotImplementedError

def load_yaml(path):
    with open(path) as f:
        text = f.read()
    return yaml.load(text)


DATA = collect_data()
KEYWORDS = all_keywords()

def answer(question: str):
    """
    Return answer for a given question.
    """
    keyword = get_keyword(question)
    if keyword not in KEYWORDS:
        return 'Dunno :('
    ans_type = expected_ans(question)
    data_files = filter(lambda x: keyword in x['keywords'],
                        DATA.values())
    possible_answers = []
    for data in data_files:
        if ans_type in data.keys():
            possible_answers.append(data[ans_type])

    # We need some kind of algo here to rate the possible answers, and return the
    # highest rated answer

    answers = rate_answers(question, possible_answers)

    return answers[0][0]
