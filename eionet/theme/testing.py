''' testing module'''
# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import eionet.theme


class EionetThemeLayer(PloneSandboxLayer):
    """EionetThemeLayer."""

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """setUpZope.

        :param app:
        :param configurationContext:
        """
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=eionet.theme)

    def setUpPloneSite(self, portal):
        """setUpPloneSite.

        :param portal:
        """
        applyProfile(portal, 'eionet.theme:default')


EIONET_THEME_FIXTURE = EionetThemeLayer()


EIONET_THEME_INTEGRATION_TESTING = IntegrationTesting(
    bases=(EIONET_THEME_FIXTURE,),
    name='EionetThemeLayer:IntegrationTesting'
)


EIONET_THEME_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(EIONET_THEME_FIXTURE,),
    name='EionetThemeLayer:FunctionalTesting'
)


EIONET_THEME_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        EIONET_THEME_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='EionetThemeLayer:AcceptanceTesting'
)
