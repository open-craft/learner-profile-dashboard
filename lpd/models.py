from django import forms
from django.core.urlresolvers import reverse
from django.db import models


class LearnerProfileDashboard(models.Model):
    name = models.TextField(help_text='Name of this LPD instance')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self).encode('utf-8')

    def get_absolute_url(self):
        return reverse('lpd:view', kwargs=dict(pk=self.id))


class LearnerProfileDashboardForm(forms.ModelForm):
    class Meta:
        model = LearnerProfileDashboard
        fields = ['name']
