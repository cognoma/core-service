# this file came from https://www.caktusgroup.com/blog/2013/06/26/media-root-and-django-tests/
# used to delete all the media files created after a test run

import os
import shutil
from django.conf import settings
from django.test.runner import DiscoverRunner


class TempMediaMixin(object):
    """
    Mixin to create MEDIA_ROOT in temp and tear down when complete.
    """

    def setup_test_environment(self):
        """
        Create temp directory and update MEDIA_ROOT and default storage.
        """
        super(TempMediaMixin, self).setup_test_environment()

    def teardown_test_environment(self):
        """
        Delete temp storage.
        """
        super(TempMediaMixin, self).teardown_test_environment()
        shutil.rmtree(settings.MEDIA_ROOT)


class TemporaryMediaTestSuiteRunner(TempMediaMixin, DiscoverRunner):
    """
    Local test suite runner.
    """