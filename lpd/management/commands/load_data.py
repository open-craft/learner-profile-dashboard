"""
Management command that populates LPD database with relevant data for 2018 iteration of HPL course
"""

import csv
import os

from django.core.management.base import BaseCommand

from lpd.constants import QuestionTypes
from lpd.models import (
    AnswerOption,
    KnowledgeComponent,
    LearnerProfileDashboard,
    LikertScaleQuestion,
    MultipleChoiceQuestion,
    QualitativeQuestion,
    RankingQuestion,
    Section,
)


# Classes

class Command(BaseCommand):
    """
    Management command that populates LPD database with relevant data for 2018 iteration of HPL course.
    """
    help = 'Management command that populates LPD database with relevant data for 2018 iteration of HPL course.'

    def add_arguments(self, parser):
        """
        Specify arguments that can be passed to this management command.
        """
        # Named (optional) arguments
        parser.add_argument(
            '--wipe-existing-data',
            action='store_true',
            dest='wipe-existing-data',
            help=(
                'Delete existing data that does not match relevant data for 2018 iteration of HPL course '
                'before populating database.'
            ),
        )

    # pylint: disable=too-many-locals
    def handle(self, *args, **options):  # noqa: MC0001
        """
        Populate LPD database with relevant data for 2018 iteration of HPL course.
        """
        if options['wipe-existing-data']:
            for model in [
                    LearnerProfileDashboard,
                    KnowledgeComponent,
                    Section,
                    QualitativeQuestion,
                    MultipleChoiceQuestion,
                    RankingQuestion,
                    LikertScaleQuestion,
                    AnswerOption,
            ]:
                model.objects.all().delete()

        # Create LPD
        lpd, _ = LearnerProfileDashboard.objects.get_or_create(name='Learner Profile')

        # Create knowledge components
        knowledge_components = {}
        with open(os.path.join(os.getcwd(), 'data', 'knowledge_components.csv'), 'rb') as kc_file:
            kc_reader = csv.reader(kc_file, quotechar='|')
            for kc_id, kc_name in kc_reader:
                knowledge_component, _ = KnowledgeComponent.objects.get_or_create(kc_id=kc_id, kc_name=kc_name)
                knowledge_components[knowledge_component.kc_id] = knowledge_component

        # Create sections
        sections = {}
        with open(os.path.join(os.getcwd(), 'data', 'sections.csv'), 'rb') as section_file:
            section_reader = csv.reader(section_file, quotechar='|')
            for section_title, intro_text in section_reader:
                section, _ = Section.objects.get_or_create(lpd=lpd, title=section_title, intro_text=intro_text)
                sections[section.order+1] = section

        # Create qualitative questions
        with open(os.path.join(os.getcwd(), 'data', 'qualitative_questions.csv'), 'rb') as qual_file:
            qual_reader = csv.reader(qual_file, quotechar='|')
            for section, number, question_text, question_type, influences_group_membership, framing_text in qual_reader:
                QualitativeQuestion.objects.get_or_create(
                    section=sections[int(section)],
                    number=int(number),
                    question_text=question_text,
                    framing_text=framing_text,
                    question_type=question_type,
                    influences_group_membership=bool(influences_group_membership),
                )

        # Create quantitative questions
        quantitative_questions = {}
        with open(os.path.join(os.getcwd(), 'data', 'quantitative_questions.csv'), 'rb') as quant_file:
            quant_reader = csv.reader(quant_file, quotechar='|')
            for section, number, question_text, question_type, randomize_options, \
                    max_options, range_min_text, range_max_text in quant_reader:
                if question_type in QuestionTypes.get_multiple_choice_types():
                    quantitative_question, _ = MultipleChoiceQuestion.objects.get_or_create(
                        section=sections[int(section)],
                        number=int(number),
                        question_text=question_text,
                        randomize_options=bool(randomize_options),
                        max_options_to_select=int(max_options),
                    )
                elif question_type == QuestionTypes.RANKING:
                    quantitative_question, _ = RankingQuestion.objects.get_or_create(
                        section=sections[int(section)],
                        number=int(number),
                        question_text=question_text,
                        randomize_options=bool(randomize_options),
                        number_of_options_to_rank=int(max_options)
                    )
                elif question_type == QuestionTypes.LIKERT:
                    quantitative_question, _ = LikertScaleQuestion.objects.get_or_create(
                        section=sections[int(section)],
                        number=int(number),
                        question_text=question_text,
                        randomize_options=bool(randomize_options),
                        answer_option_range=int(max_options),
                        range_min_text=range_min_text,
                        range_max_text=range_max_text,
                    )
                quantitative_questions[quantitative_question.section_number] = quantitative_question

        # Create answer options
        with open(os.path.join(os.getcwd(), 'data', 'answer_options.csv'), 'rb') as answer_option_file:
            answer_option_reader = csv.reader(answer_option_file, quotechar='|')
            for section_number, kc_id, option_text, allows_custom_input, influences_recommendations in \
                    answer_option_reader:
                AnswerOption.objects.create(
                    content_object=quantitative_questions[section_number],
                    knowledge_component=knowledge_components[kc_id] if kc_id else None,
                    option_text=option_text,
                    allows_custom_input=bool(allows_custom_input),
                    influences_recommendations=bool(influences_recommendations),
                )
