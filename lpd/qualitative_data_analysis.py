import re

from django.conf import settings
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer


# Globals

EXTRA_STOP_WORDS_FOR_TFIDF = [
    'education',
    'experience',
    'learn',
    'learning',
    'school',
    'students',
    'teach',
    'working'
]


# Functions

def clean_document(document):
    """
    Clean the document (by casting to lowercase and removing punctation).
    """
    document = document.lower()
    document = re.sub(r'[^\w\s]', '', document)
    return document


def make_document(answers):
    """
    Compose one document out of multiple answers.

    Clean up document and perform additional pre-processing steps before returning it.
    """
    raw_document = ' '.join(answers)
    document = clean_document(raw_document)

    # Tokenize document
    words = word_tokenize(document)

    # Perform stemming for inflected forms of "teach" root
    words_to_stem = ['teaching', 'teacher', 'teachers']
    cleaned_words = [word if word not in words_to_stem else "teach" for word in words]

    # Put document back together
    cleaned_document = ' '.join(cleaned_words)

    return cleaned_document


def make_tfidf_matrix(document):
    """
    Compose tfidf matrix (sparse word frequency matrix) of a single document.
    """
    tfidf = TfidfVectorizer(max_features=1000, stop_words='english')
    stop_words = list(tfidf.get_stop_words()) + EXTRA_STOP_WORDS_FOR_TFIDF
    tfidf.set_params(stop_words=stop_words)
    tfidf_matrix = tfidf.fit_transform(document)

    return tfidf_matrix


def calculate_probabilities(answers):
    """
    Calculates a vector of probabilities reflecting how likely a learner is
    to belong to different groups (represented by different knowledge components),
    based on the set of qualitative `answers` that the learner provided.

    Note that the set of `answers` passed to this function
    should only include answers to qualitative questions that are configured
    to influence recommendations.

    The calculations are based on LDA model that has been constructed in the past
    and is available to the app as an `lda.pkl` file in the root directory of the project.

    Returns a dictionary in the following form:
    {
        'kc_id_1': 0.2,
        'kc_id_2': 0.8
    }
    """
    document = make_document(answers)
    tfidf_matrix = make_tfidf_matrix([document])
    weights = settings.LDA_MODEL.transform(tfidf_matrix)

    probabilities = {
        settings.GROUP_KCS[index]: weight
        for index, weight in enumerate(weights)
    }

    return probabilities
