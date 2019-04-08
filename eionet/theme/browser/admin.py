import logging
import re

from lxml.etree import fromstring  # XML, XMLParer,

from DateTime import DateTime
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer as create
from Products.Five.browser import BrowserView

logger = logging.getLogger('eionet.theme.importer')

control_chars = '\x00-\x1f\x7f-\x9f'
control_char_re = re.compile('[%s]' % re.escape(control_chars))


def remove_control_chars(s):
    return control_char_re.sub('', s).replace('\f', '')


class EionetContentImporter(BrowserView):
    """ A helper class to import old content exported as XML
    """

    def __call__(self):

        if self.request.method == 'GET':
            return self.index()

        path = self.request.form.get('sourcepath')
        portal_type = self.request.form.get('portal_type')

        obj = self.context.restrictedTraverse(path)
        ranges = []
        data = obj.data

        if isinstance(data, str):
            ranges.append(data)
        else:
            while data is not None:
                ranges.append(data.data)
                data = data.next

        text = ''.join(ranges)
        text = text.decode('utf-8')
        text = remove_control_chars(text)

        tree = fromstring(text)
        importer = getattr(self, 'import_' + portal_type)

        count = importer(self.context, portal_type, tree)

        return "Imported %s objects" % count

    def import_etc_report(self, context, portal_type, tree):
        _map = {
            'teaser': ('abstract', self.as_richtext),
            'releasedate': ('publication_date', self.as_date),
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

    def as_richtext(self, value):
        return RichTextValue(value, 'text/html', 'text/html')

    def noop(self, value):
        return value

    def as_date(self, value):
        return DateTime(value).asdatetime()
