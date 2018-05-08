from ddt import ddt, data, unpack
from django.test import TestCase

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
