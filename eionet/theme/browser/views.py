''' views '''
from datetime import timedelta
import simplejson as json
from zope.size import byteDisplay
from zope.component.hooks import getSite
from zope.component import getUtility, getMultiAdapter, ComponentLookupError
from zope.interface import implementer
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
import transaction
from DateTime import DateTime
from Acquisition import aq_inner
from Products.CMFPlone.utils import safe_callable
from Products.Five.browser import BrowserView
from Products.MimetypesRegistry.interfaces import MimeTypeException
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone.interfaces.syndication import IFeedSettings
from Products.CMFCore.utils import getToolByName
from plone import api
from plone.api.content import get_state
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.textfield.value import RichTextValue
from plone.namedfile.interfaces import INamed
from plone.registry.interfaces import IRegistry
from plone.event.interfaces import IRecurrenceSupport
from eionet.theme.interfaces import ICalendarEventCreator
from eionet.theme.interfaces import ICalendarJSONSourceProvider


CATEGORIES = [
    ('events', '#5893A9', (
        ('10', 'Event'),
        ('mb', 'MB and Bureau'),
        ('nfp-eionet', 'NFP/Eionet Group'),
        ('sc', 'Scientific Committee'),
        ('nrc', 'NRC Meetings'),
        ('soer', 'SOER Events'),
    )),
    ('publications', '#F6A800', (
        ('20', 'Publication'),
        ('launch', 'Publication launch'),
        ('publication-date-tbc', 'Publication date TBC'),
    )),
    # ('#FAB9B9', (
    ('consultations', '#FF6969', (
        ('30', 'Consultation'),
        ('consult-start', 'Consultation start'),
        ('consult-per', 'Consultation period'),
        ('consult-start', 'Consultation start'),
        ('consult-end', 'Consultation end'),
    )),
    # ('#FFE524', (
    ('reporting', '#B5C132', (
        ('40', 'Reporting'),
        ('eionet-core-data', 'Eionet data flows 2020 and 2019'),
        ('report-obl', 'Reporting obligations'),
    )),
]


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
        """get_download_link.

        :param item_listing:
        """
        url = self.tabular_fielddata(item_listing, 'report_url').get('value',
                                                                     None)
        the_file = self.tabular_fielddata(item_listing, 'file').get('value',
                                                                    None)

        download_url = ''
        if the_file:
            download_url = item_listing._brain.getURL() + \
                '/@@download/file/' + the_file.filename
        if url:
            download_url = url
        return {
            'value': download_url
        }

    @property
    def collection_behavior(self):
        """collection_behavior."""
        return ICollection(aq_inner(self.context))

    @property
    def b_size(self):
        """b_size."""
        return getattr(self, '_b_size', self.collection_behavior.item_count)

    @property
    def b_start(self):
        """b_start."""
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
        contentFilter.update(
            {'sort_on': 'publication_date', 'sort_order': 'descending'})
        kwargs.setdefault('custom_query', contentFilter)
        kwargs.setdefault('batch', True)
        kwargs.setdefault('b_size', self.b_size)
        kwargs.setdefault('b_start', self.b_start)

        results = self.collection_behavior.results(**kwargs)
        return results

    def batch(self):
        ''' collection is already batched.'''
        return self.results()

    def tabular_fielddata(self, item, fieldname):
        """tabular_fielddata.

        :param item:
        :param fieldname:
        """
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
        """pas_member."""
        if not self._pas_member:
            self._pas_member = getMultiAdapter(
                (self.context, self.request),
                name='pas_member'
            )
        return self._pas_member

    @property
    def use_view_action(self):
        """use_view_action."""
        registry = getUtility(IRegistry)
        types_used = registry.get('plone.types_use_view_action_in_listings',
                                  [])
        return types_used

    @property
    def plone_view(self):
        """plone_view."""
        if not self._plone_view:
            self._plone_view = getMultiAdapter(
                (self.context, self.request),
                name='plone'
            )
        return self._plone_view

    def normalizeString(self, text):
        """normalizeString.

        :param text:
        """
        return self.plone_view.normalizeString(text)


class FrontpageNewsHelperView(BrowserView):
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

        return fields

    @property
    def plone_view(self):
        """plone_view."""
        if not self._plone_view:
            self._plone_view = getMultiAdapter(
                (self.context, self.request),
                name='plone'
            )
        return self._plone_view

    @property
    def collection_behavior(self):
        """collection_behavior."""
        return ICollection(aq_inner(self.context))

    @property
    def b_size(self):
        """b_size."""
        return getattr(self, '_b_size', self.collection_behavior.item_count)

    @property
    def b_start(self):
        """b_start."""
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
        kwargs.setdefault('custom_query', contentFilter)
        kwargs.setdefault('batch', True)
        kwargs.setdefault('b_size', self.b_size)
        kwargs.setdefault('b_start', self.b_start)

        results = self.collection_behavior.results(**kwargs)
        return results

    def batch(self):
        ''' collection is already batched.'''
        return self.results()

    def tabular_fielddata(self, item, fieldname):
        """tabular_fielddata.

        :param item:
        :param fieldname:
        """
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
        """pas_member."""
        if not self._pas_member:
            self._pas_member = getMultiAdapter(
                (self.context, self.request),
                name='pas_member'
            )
        return self._pas_member

    @property
    def use_view_action(self):
        """use_view_action."""
        registry = getUtility(IRegistry)
        types_used = registry.get('plone.types_use_view_action_in_listings',
                                  [])
        return types_used

    def normalizeString(self, text):
        """normalizeString.

        :param text:
        """
        return self.plone_view.normalizeString(text)


class ReportView(BrowserView):
    """ Custom class for report view
    """

    @property
    def _mimetype(self):
        """_mimetype."""
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

        if mimetypes:
            return mimetypes[0]
        return None

    @property
    def file_size(self):
        """file_size."""
        if INamed.providedBy(self.context.file):
            return byteDisplay(self.context.file.getSize())
        return "0 KB"

    @property
    def file_icon(self):
        """file_icon."""
        if not self.context.file:
            return None

        mimetype = self._mimetype
        if mimetype and mimetype.icon_path:
            return "%s/%s" % (getToolByName(getSite(), 'portal_url')(),
                              mimetype.icon_path)
        return None


class GoPDB(BrowserView):
    """GoPDB."""

    def __call__(self):
        import pdb
        pdb.set_trace()


class CalendarView(BrowserView):
    """ The class is needed to register a viewlet for this view.
    """
    def first_day(self):
        """
        Returns the first day of the week as an integer.
        """
        calendar_tool = getToolByName(self.context, 'portal_calendar', None)
        if calendar_tool:
            first = calendar_tool.getFirstWeekDay()
        else:
            first = getSite().portal_registry['plone.first_weekday']
        return (first + 1) if first < 6 else 0

    def can_add_content(self):
        """ check if there is an adapter defined for adding events from
            the fullcalendar interface"""
        try:
            eventCreator = getMultiAdapter((self.context, self.request),
                                           ICalendarEventCreator)
        except ComponentLookupError:
            return False

        return eventCreator.getEventType() in \
            self.context.getImmediatelyAddableTypes()


@implementer(ICalendarJSONSourceProvider)
class CalendarJSONSource(object):
    """CalendarJSONSource"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.memberid = \
            self.context.portal_membership.getAuthenticatedMember().id

    def generate_json_calendar_source(self):
        """generate json with events as calendar source."""
        result = []

        for brain in self.get_event_brains():
            event = brain.getObject()
            view = self.request.get('view')
            if view != 'calendar_view' and not (event.tag or event.subject):
                # events with no tag or subject belong only on the main view
                continue
            for view_id, _color, categories in CATEGORIES:
                if view == view_id:
                    if event.tag and categories[0][0] not in event.tag:
                        break
                    # support for events import from ICS, but tag takes
                    # precedence
                    if event.subject:
                        if not set(
                            [subject.lower() for subject in event.subject]) & \
                            set(category[0]
                                for category in categories[1:]):
                            break
            else:
                result.extend(self.generate_source_dict_from_event(event))

        return json.dumps(result, sort_keys=True)

    def get_event_brains(self):
        """get_event_brains."""
        args = {
            'start': {
                'query': DateTime(self.request.get('end')), 'range': 'max'},
            'end': {
                'query': DateTime(self.request.get('start')), 'range': 'min'}}
        if self.context.portal_type in ['Topic', 'Collection']:
            return self.context.aq_inner.queryCatalog(args)
        catalog = getToolByName(self.context, 'portal_catalog')
        portal_calendar = getToolByName(self.context, 'portal_calendar',
                                        None)
        if portal_calendar:
            args['portal_type'] = portal_calendar.getCalendarTypes()

        return catalog(
            path={'depth': -1,
                  'query': '/'.join(self.context.getPhysicalPath())},
            **args
        )

    def generate_source_dict_from_event(self, event):
        """generate_source_dict_from_event.

        :param event:
        """
        view = self.request.get('view')
        ret = []
        title = event.Title()
        description = event.Description()

        if event.text:
            description = event.text.output
        editable = api.user.has_permission('Modify portal content', obj=event)
        deletable = api.user.has_permission('Delete objects', obj=event)
        color = 'grey'
        if event.tag:
            for _view_type, group_color, categories in CATEGORIES:
                for cat_id, _cat_title in categories:
                    if cat_id in event.tag:
                        color = group_color
                        break
        else:
            # for events imported from ICS
            for _view_type, group_color, categories in CATEGORIES:
                for cat_id, _cat_tile in categories:
                    for tag in event.subject:
                        if cat_id == tag.lower():
                            color = group_color
                            break

        adapter = IRecurrenceSupport(event)
        # get all occurrences of the current event (if not recurrent,
        # the generator will only produce the event itself) and create a
        # results entry for each one
        for occurrence in adapter.occurrences(
                range_start=DateTime(self.request.get('start')),
                range_end=DateTime(self.request.get('end'))):
            # The default source marks an event as all day if it is longer than
            # one day. Marking an event as all day in contentpage will set
            # the times to 00:00 and 23:59. If those times are on the same
            # date they will not be recognised as all day because that's only a
            # 0.999.. day. This check will mark those events as all day.
            start = occurrence.start
            end = occurrence.end
            duration = occurrence.end - occurrence.start
            if isinstance(duration, timedelta):
                duration = duration.total_seconds() / 60. / 60. / 24.
            # compute real all day for the tooltip information
            real_allday = (event.whole_day or
                           duration > 0.99 or
                           start == end or
                           occurrence.start.date() != occurrence.end.date())
            # For the main calendar_view we set all events to allday because we
            # don't show start and end times anyway and we need the background
            # color that only appears on full day events.
            if view == 'calendar_view':
                allday = True
                end += timedelta(days=1)
            else:
                # on all other views we need the allday to be correct
                allday = real_allday
            iso = 'isoformat' if hasattr(start, 'isoformat') else 'ISO8601'
            start = getattr(start, iso)()
            end = getattr(end, iso)()

            ret.append({
                "id": "UID_%s" % (event.UID()),
                "title": title,
                "start": start,
                "end": end,
                "url": event.absolute_url(),
                "can_edit": editable,
                "can_delete": deletable,
                "backgroundColor": color,
                "allDay": allday,
                "realAllDay": real_allday,
                "className": "state-" + str(get_state(event)) +
                (editable and " editable" or ""),
                "description": description,
                "location": event.location,
                "realStartTime": occurrence.start.strftime('%H:%M'),
                "realEndTime": occurrence.end.strftime('%H:%M'),
                "realStartDate": occurrence.start.strftime('%B %d'),
                "realEndDate": occurrence.end.strftime('%B %d'),
                "oneday": occurrence.start.date() == occurrence.end.date()
            })
        return ret


class CalendarupdateView(BrowserView):
    """ Calendarupdate browser view
    """

    def __call__(self, *args, **kw):
        """Render JS Initialization code"""

        response = self.request.response

        source_provider = getMultiAdapter((self.context, self.request),
                                          name='calendar_source')

        response.setHeader('Content-Type', 'application/json')
        return source_provider.generate_json_calendar_source()


class CalendarDropView(BrowserView):
    """ view that handles moving events to another date in the callendar"""

    def __call__(self):
        request = self.context.REQUEST

        event_uid = request.get('event')

        if event_uid:
            event_uid = event_uid.split('UID_')[1]
        brains = self.context.portal_catalog(UID=event_uid)

        obj = brains[0].getObject()
        startDate, endDate = obj.startDate, obj.endDate
        dayDelta, minuteDelta = (float(request.get('dayDelta')),
                                 float(request.get('minuteDelta')))

        startDate = startDate + dayDelta + minuteDelta / 1440.0
        endDate = endDate + dayDelta + minuteDelta / 1440.0

        obj.setStartDate(startDate)
        obj.setEndDate(endDate)
        obj.reindexObject()
        return True


class CalendarResizeView(BrowserView):
    """ view that handles changing the event duration from the calendar"""

    def __call__(self):
        request = self.context.REQUEST
        event_uid = request.get('event')
        if event_uid:
            event_uid = event_uid.split('UID_')[1]
        brains = self.context.portal_catalog(UID=event_uid)
        obj = brains[0].getObject()
        endDate = obj.endDate
        dayDelta, minuteDelta = (float(request.get('dayDelta')),
                                 float(request.get('minuteDelta')))

        endDate = endDate + dayDelta + minuteDelta / 1440.0

        obj.setEndDate(endDate)
        obj.reindexObject()
        return True


class CalendarAddView(BrowserView):
    """ handle adding of events from the calendar interface"""

    def __call__(self):
        request = self.context.REQUEST
        title = request.get('title')
        start_date = DateTime(int(request.get('startdate')))

        if not title or not start_date:
            raise ValueError()

        eventCreator = getMultiAdapter((self.context, request),
                                       ICalendarEventCreator)
        event = eventCreator.createEvent(title, start_date)

        self.request.RESPONSE.redirect(event.absolute_url() + '/edit')


class CategoriesVocabularyFactory(object):
    """ CategoriesVocabularyFactory """

    def __call__(self, context):

        return SimpleVocabulary(
            [SimpleTerm(value=cat[2][0][0], title=cat[2][0][1]) for
                cat in CATEGORIES])


class EventsDescription2Text(BrowserView):
    """Move the text from description to the RichText text field"""

    def __call__(self):
        count = 0
        REQUEST = self.request
        transforms = getToolByName(getSite(), 'portal_transforms')
        for event in self.context.objectValues():
            if event.portal_type == 'Event' and event.description:
                html = transforms.convertTo(
                    'text/html', event.description,
                    mimetype='text/structured').getData()
                event.text = RichTextValue(html,
                                           'text/html',
                                           'text/html')
                event.description = ''
                event._p_changed = True
                count += 1
        if count:
            transaction.commit()
        IStatusMessage(REQUEST).add(
            '%s events updated' % count, 'info')
        REQUEST.RESPONSE.redirect(self.context.absolute_url())


class DisableRSS(BrowserView):
    """ Disable the RSS link on the planner folder """

    def __call__(self):
        settings = IFeedSettings(self.context)
        settings.enabled = False
        settings._p_changed = True
        transaction.commit()
        IStatusMessage(self.request).add('RSS disabled on %s' %
                                         self.context.getId())
        self.request.RESPONSE.redirect(self.context.absolute_url())


class EnableRSS(BrowserView):
    """ Enable the RSS link on the planner folder """

    def __call__(self):
        settings = IFeedSettings(self.context)
        settings.enabled = True
        settings._p_changed = True
        transaction.commit()
        IStatusMessage(self.request).add('RSS enabled on %s' %
                                         self.context.getId())
        self.request.RESPONSE.redirect(self.context.absolute_url())
