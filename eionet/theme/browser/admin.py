import logging
from HTMLParser import HTMLParser
from StringIO import StringIO

from lxml.etree import fromstring  # XML, XMLParer,
from lxml.html import fragment_fromstring
from lxml.html.clean import clean_html

from DateTime import DateTime
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer as create
from plone.namedfile.file import NamedBlobFile
from Products.Five.browser import BrowserView

logger = logging.getLogger('eionet.theme.importer')


def read_data(obj_file):
    ranges = []
    data = obj_file.data

    if isinstance(data, str):
        ranges.append(data)
    else:
        while data is not None:
            ranges.append(data.data)
            data = data.next

    return ''.join(ranges)


class EionetContentImporter(BrowserView):
    """ A helper class to import old content exported as XML
    """

    def __call__(self):

        if self.request.method == 'GET':
            return self.index()

        path = self.request.form.get('sourcepath')
        portal_type = self.request.form.get('portal_type')

        obj = self.context.restrictedTraverse(path)

        text = read_data(obj)
        text = text.replace('\f', '')        # line feed, weird
        text = text.decode('utf-8')

        tree = fromstring(text)
        importer = getattr(self, 'import_' + portal_type)

        count = importer(self.context, portal_type, tree)

        return "Imported %s objects" % count

    def import_etc_report(self, context, portal_type, tree):
        _map = {
            'teaser': ('abstract', self.as_richtext),
            'releasedate': ('publication_date', self.as_date),
            'title': ('title', self.as_plain_text),
        }
        count = 0

        for node in tree.xpath('object'):
            url = node.get('url')
            id = url.rsplit('/', 1)[-1]
            props = {}

            for ep in node.findall('prop'):
                pname = ep.get('name')

                if pname in _map:
                    pname, convert = _map[pname]
                else:
                    convert = self.noop

                text = ep.text or ''
                props[pname] = convert(text.strip())

            try:
                obj = create(context, portal_type, id=id, **props)
            except ValueError:      # this is due to id error
                obj = create(context, portal_type, **props)
                logger.warning("Changed id for object: %s", id)

            logger.info("Imported %s", obj.absolute_url())
            count += 1

        return count

    def as_plain_text(self, value):
        value = HTMLParser().unescape(value)
        value = u"<div>%s</div>" % value
        el = fragment_fromstring(value)
        texts = el.xpath('text()')

        return u' '.join(texts)

    def as_richtext(self, value):
        if value:
            value = clean_html(value)

        return RichTextValue(value, 'text/html', 'text/html')

    def noop(self, value):
        return value

    def as_date(self, value):
        return DateTime(value).asdatetime()


class EionetStructureImporter(BrowserView):
    """ A helper class to import old Zope content and recreate as Plone content
    """

    def __call__(self):
        if self.request.method == 'GET':
            return self.index()

        path = self.request.form.get('sourcepath')
        source = self.context.restrictedTraverse(path)

        return self.import_generic(source, self.context)

    def import_generic(self, source, destination):
        destination = self.context

        for obj in source.objectValues():
            handler = getattr(self, 'import_' + obj.meta_type)
            handler(obj, destination)

        return

    def import_File(self, obj, destination):
        data = read_data(obj)
        fobj = NamedBlobFile(data=data, contentType=obj.content_type,
                             filename=obj.getId())

        props = {
            'file': fobj,
            'title': obj.title,
            'id': obj.getId(),
        }

        imported = create(destination, 'File', props)

        return imported

    def import_Folder(self, obj, destination):
        title = obj.title
        id = obj.getId()
        folder = create(destination, 'Folder', id=id, title=title)

        for child in obj.objectValues():
            handler = getattr(self, 'import_' + obj.meta_type)
            handler(obj, folder)

        return folder
