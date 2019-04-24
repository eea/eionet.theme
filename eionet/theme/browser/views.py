from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.contenttypes.browser.collection import CollectionView


class ReportView(CollectionView):
    """ Custom class for report view
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


class GoPDB(BrowserView):
    def __call__(self):
        import pdb;pdb.set_trace()
