import logging
from Products.Five.browser import BrowserView
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
