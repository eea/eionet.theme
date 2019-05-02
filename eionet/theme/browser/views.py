from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.MimetypesRegistry.interfaces import MimeTypeException
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.contenttypes.browser.collection import CollectionView
from plone.namedfile.interfaces import INamed
from zope.size import byteDisplay
from zope.component.hooks import getSite


class CollectionReportView(CollectionView):
    """ Custom class for collection report view
    """

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

    def normalize_fields(self, field):
        names = {
            'report_url': 'Download',
            'publication_date': 'Publication date'
        }
        return names.get(field, field)

    # sort_on='sortable_title', sort_order='ascending'

    def batch(self):
        # collection is already batched.
        kwargs = {'sort_on': 'publication_date'}
        return self.results(**kwargs)


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
