''' overrides module '''
import logging
from zope.component import getMultiAdapter, getUtility
from zope.schema.interfaces import IVocabularyFactory
from Acquisition import aq_inner
from icalendar.prop import vText
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import PathBarViewlet as ViewletBase
from plone.app.textfield.value import RichTextValue
from plone.app.textfield.interfaces import ITransformer

logger = logging.getLogger('eionet.theme.overrides')


class PathBarViewlet(ViewletBase):
    """PathBarViewlet."""

    index = ViewPageTemplateFile('overrides/path_bar.pt')

    def update(self):
        """update."""
        super(PathBarViewlet, self).update()

        self.is_rtl = self.portal_state.is_rtl()

        breadcrumbs_view = getMultiAdapter((self.context, self.request),
                                           name='breadcrumbs_view')
        self.breadcrumbs = breadcrumbs_view.breadcrumbs()

    def get_home(self):
        """get_home."""
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


def apply_patched_property(scope, original, replacement):
    """ Apply patched property """
    setattr(scope, original, replacement())


def description(self):
    """ Patch description to contain html to text from the text property """
    transformer = ITransformer(self.context)
    text = self.context.text or self.context.description
    if isinstance(text, RichTextValue):
        text = text.raw
    text = text.replace('<br>', '\n').replace('</p>', '</p>\n')
    if '<' in text:
        rich = RichTextValue(text, 'text/html', 'text/html')
    else:
        rich = RichTextValue(text, 'text/plain', 'text/html')

    return {'value': transformer(rich, 'text/plain')}


patched_description = lambda: property(description)  # noqa: E731


def categories(self):
    """ Patch categories to include our custom tags values """
    ret = []
    if self.context.tag:
        factory = getUtility(IVocabularyFactory,
                             'eionet.fullcalendar.categories')
        vocabulary = factory(self.context)
        ret.append(vText(vocabulary.getTerm(self.context.tag).title))
    for cat in self.event.subjects or []:
        ret.append(cat)
    if ret:
        return {'value': ret}
    return None


patched_categories = lambda: property(categories)  # noqa: E731
