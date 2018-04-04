from django.views.generic import DetailView, ListView, CreateView, UpdateView
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from lpd.models import LearnerProfileDashboard, LearnerProfileDashboardForm


class LPDView(TemplateView):
    """
    Display LPD.
    """
    template_name = 'view.html'

    def get_context_data(self, **kwargs):
        """
        Collect necessary information for displaying LPD.
        """
        context = super(LPDView, self).get_context_data(**kwargs)
        lpd = LearnerProfileDashboard.objects.get()
        context['lpd'] = lpd
        return context


class LearnerProfileDashboardView(object):
    model = LearnerProfileDashboard
    form_class = LearnerProfileDashboardForm


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
