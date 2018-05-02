import re

from django.conf import settings
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer


EXTRA_STOP_WORDS_FOR_TFIDF = ['education', 'students', 'students', 'school',
                              'learning', 'learn', 'experience', 'teach',
                              'working']

lda = settings.LDA_MODEL


def clean_doc(document):
    """
    Clean the document (by casting to lowercase and removing punctation).
    """
    document = document.lower()
    document = re.sub(r'[^\w\s]', '', document)
    return document


def make_doc(answers):
    """
    Compose one document out of multiple answers.
    """
    clean = clean_doc(" ".join(answers))
    words = word_tokenize(clean)

    # reduce instances of "teach-" to "teach"
    t = ['teaching', 'teacher', 'teachers']
    cleaner = [i if i not in t else "teach" for i in words]
    doc = " ".join(cleaner)

    return doc


def make_tfidf_matrix(doc):
    """
    Compose tfidf matrix (sparse word frequency matrix) of a single document.
    """
    tfidf = TfidfVectorizer(max_features=1000, stop_words='english')
    stops = list(tfidf.get_stop_words()) + EXTRA_STOP_WORDS_FOR_TFIDF
    tfidf.set_params(stop_words=stops)
    tfidf_matrix = tfidf.fit_transform(doc)

    return tfidf_matrix


def calculate_probabilities(answers):
    """
    Calculates a vector of probabilities reflecting how likely learner is
    to belong to the different groups (different knowledge components).

    The calculations are based on LDA model that have been constructed in the past
    and should be added to the project as `lda.pkl` file in the root directory.

    Returns a dictionary in the following form:
    {
        'kc_id_1': 0.2,
        'kc_id_2': 0.8
    }
    """
    doc = make_doc(answers)
    tfidf_matrix = make_tfidf_matrix([doc])
    weights = lda.transform(tfidf_matrix)

    probabilities = {
        settings.GROUPS_KCS[id]: weight
        for id, weight in enumerate(weights)
    }

    return probabilities
