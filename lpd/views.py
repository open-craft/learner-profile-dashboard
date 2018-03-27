from django.views.generic import DetailView, ListView, CreateView, RedirectView, UpdateView
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from lpd.models import LearnerProfileDashboard, LearnerProfileDashboardForm


class LearnerProfileDashboardView(object):
    model = LearnerProfileDashboard
    form_class = LearnerProfileDashboardForm


class ShowOrCreateLearnerProfileDashboardView(LearnerProfileDashboardView, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):  # pylint: disable=inconsistent-return-statements
        lpd = LearnerProfileDashboard.objects.values_list('id', flat=True)
        if len(lpd) > 1:
            return reverse('lpd:list')
        elif len(lpd) == 1:
            return reverse('lpd:view', kwargs=dict(pk=lpd[0]))
        elif len(lpd) == 0:  # pylint: disable=len-as-condition
            return reverse('lpd:add')


class ShowLearnerProfileDashboardView(LearnerProfileDashboardView, DetailView):
    template_name = 'view.html'


class ListLearnerProfileDashboardView(LearnerProfileDashboardView, ListView):
    template_name = 'list.html'
    paginate_by = 12
    paginate_orphans = 2


class CreateLearnerProfileDashboardView(LearnerProfileDashboardView, CreateView):
    template_name = 'edit.html'

    '''Login required for all posts'''
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        return super(CreateLearnerProfileDashboardView, self).post(request, *args, **kwargs)


class UpdateLearnerProfileDashboardView(LearnerProfileDashboardView, UpdateView):
    template_name = 'edit.html'

    '''Login required for all posts'''
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        return super(UpdateLearnerProfileDashboardView, self).post(request, *args, **kwargs)
