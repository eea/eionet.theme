# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from eionet.theme.testing import EIONET_THEME_INTEGRATION_TESTING
from Products.CMFPlone.utils import get_installer

import unittest


class TestSetup(unittest.TestCase):
    """Test that eionet.theme is properly installed."""

    layer = EIONET_THEME_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = get_installer(self.portal)

    def test_product_installed(self):
        """Test if eionet.theme is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'eionet.theme'))

    def test_browserlayer(self):
        """Test that IEionetThemeLayer is registered."""
        from eionet.theme.interfaces import (
            IEionetThemeLayer)
        from plone.browserlayer import utils
        self.assertIn(IEionetThemeLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = EIONET_THEME_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = get_installer(self.portal)
        self.installer.uninstallProducts(['eionet.theme'])

    def test_product_uninstalled(self):
        """Test if eionet.theme is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'eionet.theme'))

    def test_browserlayer_removed(self):
        """Test that IEionetThemeLayer is removed."""
        from eionet.theme.interfaces import \
            IEionetThemeLayer
        from plone.browserlayer import utils
        self.assertNotIn(IEionetThemeLayer, utils.registered_layers())
