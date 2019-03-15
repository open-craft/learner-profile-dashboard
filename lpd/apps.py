"""
AppConfig for LPD.
"""

from django.apps import AppConfig


class LearnerProfileDashboardConfig(AppConfig):
    """
    AppConfig for LPD.
    """
    name = "lpd"
    verbose_name = "Learner Profile Dashboard"

    def ready(self):
        """
        Perform initialization logic.
        """
        from django_lti_tool_provider.views import LTIView
        from lpd.auth import ApplicationHookManager

        LTIView.register_authentication_manager(ApplicationHookManager())
