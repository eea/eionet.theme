import logging
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import PathBarViewlet as ViewletBase
from zope.component import getMultiAdapter

logger = logging.getLogger('eionet.theme.overrides')


class PathBarViewlet(ViewletBase):
    index = ViewPageTemplateFile('overrides/path_bar.pt')

    def update(self):
        super(PathBarViewlet, self).update()

        self.is_rtl = self.portal_state.is_rtl()

        breadcrumbs_view = getMultiAdapter((self.context, self.request),
                                           name='breadcrumbs_view')
        self.breadcrumbs = breadcrumbs_view.breadcrumbs()

    def get_home(self):
        tab_action = self.context.portal_actions.get('portal_tabs')
        return tab_action.index_html.title


def patched_toLocalizedTime(self, time, long_format=None, time_only=None):
    """ Monkey patched Convert time to localized time
    """
    context = aq_inner(self.context)

    if context.portal_type in ['Collection']:
        long_format = 0

    util = getToolByName(context, 'translation_service')
    loc_time = util.ulocalized_time(time, long_format, time_only,
                                    context=context, domain='plonelocales',
                                    request=self.request)
    loc_time = loc_time.replace(',', '')
    return loc_time
