from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_callable
from Products.Five.browser import BrowserView
from Products.MimetypesRegistry.interfaces import MimeTypeException
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.contenttypes.browser.collection import CollectionView
from plone.namedfile.interfaces import INamed
from plone.registry.interfaces import IRegistry
from zope.size import byteDisplay
from zope.component.hooks import getSite
from zope.component import getUtility, getMultiAdapter


class CollectionHelperView(BrowserView):
    """ Custom class for collection helper view
    """
    text_class = None
    _plone_view = None
    _portal_state = None
    _pas_member = None

    def tabular_fields(self):
        """ Returns a list of all metadata fields from the catalog that were
            selected.
        """
        context = aq_inner(self.context)
        wrapped = ICollection(context)
        fields = wrapped.selectedViewFields()
        fields = [field[0] for field in fields]

        fields.append('report_url')
        return fields

    def get_download_link(self, item_listing):
        url = self.tabular_fielddata(item_listing, 'report_url').get('value', None)
        file = self.tabular_fielddata(item_listing, 'file').get('value', None)

        download_url = ''
        if file:
            download_url = item_listing._brain.getURL() + '/@@download/file/' + file.filename
        if url:
            download_url = url
        return {
            'value': download_url
        }

    @property
    def collection_behavior(self):
        return ICollection(aq_inner(self.context))

    @property
    def b_size(self):
        return getattr(self, '_b_size', self.collection_behavior.item_count)

    @property
    def b_start(self):
        b_start = getattr(self.request, 'b_start', None) or 0
        return int(b_start)

    def results(self, **kwargs):
        """Return a content listing based result set with results from the
        collection query.
        :param **kwargs: Any keyword argument, which can be used for catalog
                         queries.
        :type  **kwargs: keyword argument
        :returns: plone.app.contentlisting based result set.
        :rtype: ``plone.app.contentlisting.interfaces.IContentListing`` based
                sequence.
        """
        # Extra filter
        contentFilter = dict(self.request.get('contentFilter', {}))
        contentFilter.update(kwargs.get('contentFilter', {}))
        contentFilter.update({'sort_on': 'publication_date', 'sort_order': 'descending'})
        kwargs.setdefault('custom_query', contentFilter)
        kwargs.setdefault('batch', True)
        kwargs.setdefault('b_size', self.b_size)
        kwargs.setdefault('b_start', self.b_start)

        results = self.collection_behavior.results(**kwargs)
        return results

    def batch(self):
        # collection is already batched.
        return self.results()


    def tabular_fielddata(self, item, fieldname):
        value = getattr(item, fieldname, '')
        if safe_callable(value):
            value = value()
        if fieldname in [
                'CreationDate',
                'ModificationDate',
                'Date',
                'EffectiveDate',
                'ExpirationDate',
                'effective',
                'expires',
                'start',
                'end',
                'created',
                'modified',
                'last_comment_date']:
            value = self.context.toLocalizedTime(value, long_format=1)

        return {
            # 'title': _(fieldname, default=fieldname),
            'value': value
        }

    @property
    def pas_member(self):
        if not self._pas_member:
            self._pas_member = getMultiAdapter(
                (self.context, self.request),
                name=u'pas_member'
            )
        return self._pas_member

    @property
    def use_view_action(self):
        registry = getUtility(IRegistry)
        types_used = registry.get('plone.types_use_view_action_in_listings', [])
        return types_used


class ReportView(BrowserView):
    """ Custom class for report view
    """

    @property
    def _mimetype(self):
        registry = getToolByName(self.context, 'mimetypes_registry', None)
        if not registry:
            return None
        try:
            content_type = self.context.file.contentType
            mimetypes = registry.lookup(content_type)
        except AttributeError:
            mimetypes = [registry.lookupExtension(self.context.file.filename)]
        except MimeTypeException:
            return None

        if len(mimetypes):
            return mimetypes[0]
        else:
            return None

    @property
    def file_size(self):
        if INamed.providedBy(self.context.file):
            return byteDisplay(self.context.file.getSize())
        else:
            return "0 KB"

    @property
    def file_icon(self):
        if not self.context.file:
            return None

        mimetype = self._mimetype
        if mimetype and mimetype.icon_path:
            return "%s/%s" % (getToolByName(getSite(), 'portal_url')(),
                              mimetype.icon_path)
        else:
            return None


class GoPDB(BrowserView):
    def __call__(self):
        import pdb;pdb.set_trace()
