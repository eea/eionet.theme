''' externaltemplates module '''
from plone import api
from plone.app.theming.interfaces import IThemeSettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class ExternalTemplateHeader():
    """ExternalTemplateHeader."""

    def theme_base_url(self):
        """theme_base_url."""
        reg = getUtility(IRegistry)
        settings = reg.forInterface(IThemeSettings, False)
        portal = api.portal.get()
        base_url = portal.absolute_url()

        return base_url + '/++theme++' + settings.currentTheme + '/'

    def theme_base(self):
        """theme_base."""
        reg = getUtility(IRegistry)
        settings = reg.forInterface(IThemeSettings, False)

        return '/++theme++' + settings.currentTheme + '/'
