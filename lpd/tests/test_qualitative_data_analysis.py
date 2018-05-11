import os

from ddt import ddt, data, unpack
from django.test import override_settings, TestCase
from sklearn.externals import joblib

from lpd import qualitative_data_analysis as qda


@ddt
class QualtitiveDataAnalysisTestCase(TestCase):
    """Tests for qualitative data analysis."""

    @data(
        (
            (
                'The Walrus and the Carpenter Were walking close at hand; '
                'They wept like anything to see Such quantities of sand: '
                '"If this were only cleared away," They said, "it would be grand!"'
            ),
            (
                'the walrus and the carpenter were walking close at hand '
                'they wept like anything to see such quantities of sand '
                'if this were only cleared away they said it would be grand'
            ),
        )
    )
    @unpack
    def test_clean_document(self, document, expected_after_cleaning):
        """
        Test that `clean_document` correctly lower-cases `document` and removes punctuation from it.
        """
        self.assertEqual(qda.clean_document(document), expected_after_cleaning)

    @data(
        (
            [
                (
                    'When the Teacher entered the class \'twas brillig, '
                    'and the slithy toves Did gyre and gimble in the wabe.'
                ),
                '"See how eagerly the lobsters and the turtles all advance!", said a Teacher, teaching a snail.'
            ],
            (
                'when the teach entered the class twas brillig and the slithy toves did gyre and gimble in the wabe '
                'see how eagerly the lobsters and the turtles all advance said a teach teach a snail'
            )
        )
    )
    @unpack
    def test_make_document(self, answers, expected_document):
        """
        Test that `make_document` correctly combines `answers`
        and performs stemming for inflected forms of 'teach' root.
        """
        self.assertEqual(qda.make_document(answers), expected_document)

    @data(
        (
            [
                'Teaching is awesome, I love it.',
                'I have many teachers in my family, I thought of becoming one.',
                'I would love to remove gaps among marginalized social groups.',
                (
                    'I need to improve my knowledge and skill, having worked in different places in the world,'
                    'I\'ve gathered better understanding of different cultures.'
                )
            ],
            {
                'kc_id_1': 0.03020547,
                'kc_id_2': 0.0302166,
                'kc_id_3': 0.03020543,
                'kc_id_4': 0.03020937,
                'kc_id_5': 0.03021411,
                'kc_id_6': 0.81875085,
                'kc_id_7': 0.03019817,
            }
        )
    )
    @unpack
    @override_settings(
        LDA_MODEL=joblib.load(
            os.path.join(os.path.dirname(__file__), 'lda_test.pkl')
        )
    )
    @override_settings(
        TFIDF_VECTORIZER=joblib.load(
            os.path.join(os.path.dirname(__file__), 'tfidf_vectorizer_test.pkl')
        )
    )
    @override_settings(
        GROUP_KCS=[
            'kc_id_1', 'kc_id_2', 'kc_id_3',
            'kc_id_4', 'kc_id_5', 'kc_id_6',
            'kc_id_7'
        ]
    )
    def test_calculate_probabilities(self, answers, expected_probabilities):
        """
        Tests that `calculate_probabilities` produces correct dictionary
        of the following form:
        {knowledge components:
        probabilities of user belonging to groups represented by the knowledge components}
        Assures that the calculated probabilities are correct.
        """
        probabilities = qda.calculate_probabilities(answers)
        self.assertEqual(
            expected_probabilities.keys(),
            probabilities.keys()
        )
        for group_kc_id, probability in probabilities.items():
            expected_probability = expected_probabilities[group_kc_id]
            self.assertAlmostEqual(probability, expected_probability, 5)
