"""
Django admin for Learner Profile Dashboard
"""

from django.contrib import admin

from .models import (
    AnswerOption,
    KnowledgeComponent,
    LearnerProfileDashboard,
    LikertScaleQuestion,
    MultipleChoiceQuestion,
    QualitativeQuestion,
    RankingQuestion,
    Section,
)

admin.site.register(LearnerProfileDashboard)
admin.site.register(Section)
admin.site.register(QualitativeQuestion)
admin.site.register(MultipleChoiceQuestion)
admin.site.register(RankingQuestion)
admin.site.register(LikertScaleQuestion)
admin.site.register(AnswerOption)
admin.site.register(KnowledgeComponent)
