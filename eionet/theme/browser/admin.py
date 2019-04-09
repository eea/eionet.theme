import logging
from HTMLParser import HTMLParser

from lxml.etree import fromstring as etree_fromstring
from lxml.html import fragment_fromstring, fromstring, tostring
from lxml.html.clean import clean_html

import transaction
from DateTime import DateTime
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer as create
from plone.namedfile.file import NamedBlobFile
from Products.Five.browser import BrowserView

logger = logging.getLogger('eionet.theme.importer')

DEBUG = True


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


class DummyDict:
    """ A "request" substitute that renders all DTML vars as empty strings
    """

    def __getitem__(self, key):
        return ''


def as_plain_text(value):
    value = HTMLParser().unescape(value)
    value = u"<div>%s</div>" % value
    el = fragment_fromstring(value)
    texts = el.xpath('text()')

    return u' '.join(texts)


def as_richtext(value):
    if value:
        value = clean_html(value)

    return RichTextValue(value, 'text/html', 'text/html')


def noop(value):
    return value


def as_date(value):
    return DateTime(value).asdatetime()


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

        tree = etree_fromstring(text)
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


class EionetStructureImporter(BrowserView):
    """ A helper class to import old Zope content and recreate as Plone content
    """

    def __call__(self):
        if self.request.method == 'GET':
            return self.index()

        path = self.request.form.get('sourcepath')
        source = self.context.restrictedTraverse(path)

        dest = self.import_location(source, self.context)
        logger.info("Finished import")

        return "Finished import: %s" % dest.absolute_url()

    def import_location(self, source, destination):
        for obj in source.objectValues():
            metatype = obj.meta_type.replace(' ', '')
            handler = getattr(self, 'import_' + metatype, None)

            if handler is None:
                raise ValueError('Not supported: %s (%s)' % (obj.getId(),
                                                             metatype))
            handler(obj, destination)

        if not DEBUG:
            transaction.commit()

        return destination

    def import_File(self, obj, destination):
        return
        data = read_data(obj)
        fobj = NamedBlobFile(data=data, contentType=obj.content_type,
                             filename=unicode(obj.getId()))

        props = {
            'file': fobj,
            'title': as_plain_text(obj.title),
            'id': obj.getId(),
        }

        obj = create(destination, 'File', **props)
        logger.info("Created file: %s", obj.absolute_url())

        if not DEBUG:
            transaction.commit()

        return obj

    def import_Image(self, obj, destination):
        return self.import_File(obj, destination)

    def import_Folder(self, obj, destination):
        folder = create(destination, 'Folder', id=obj.getId(),
                        title=as_plain_text(obj.title))
        logger.info("Created folder: %s", obj.absolute_url())

        return self.import_location(obj, folder)

    def import_DTMLDocument(self, obj, destination):
        text = obj(REQUEST=DummyDict())

        title = obj.title
        title = unicode(title).strip()
        title = as_plain_text(title)

        page = self._create_page(destination, obj.getId(), title, text)

        if page is not None:
            logger.info("Created page: %s", page.absolute_url())

        return page

    def import_DTMLMethod(self, obj, destination):
        return self.import_DTMLDocument(obj, destination)

    def _create_page(self, destination, id, title, html):
        if not id == 'airview.html':
            return

        if html:
            html = clean_html(html).decode('utf-8')
            tree = fromstring(html)
            h1s = tree.xpath('h1')

            if h1s:
                h1 = h1s[0]
                h1.drop_tree()
                new_title = h1.text_content().strip()
                logger.info("Replacing title: %s -:- %s", title, new_title)
                # TODO: handle multiple spaces in text
                title = new_title

            html = tostring(tree)

        rt = RichTextValue(html, 'text/html', 'text/html')

        return create(destination, 'Document', id=id, title=title, text=rt)

    def import_SiteErrorLog(self, obj, destination):
        return destination
