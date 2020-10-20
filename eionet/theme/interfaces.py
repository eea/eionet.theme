# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface


class IEionetThemeLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IEionetGenericThemeLayer(IEionetThemeLayer):
    """Marker interface that defines a browser layer."""


class ICalendarLayer(Interface):
    """Marker interface that defines a browser layer."""


class ICalendarJSONSourceProvider(Interface):
    """ Provides the JSON source to fill the calendar with events.
    """

    def generate_json_calendar_source():
        """ Calls the following methods to get the calendar source and returns
            is as JSON.
        """

    def get_event_brains():
        """ Returns list of brains to display in the current calendar view.
        """

    def generate_source_dict_from_brain(brain):
        """ Reads the relevant information from the brain and generates a dict
            based on thos informations. This dict is later converted to JSON.
        """


class ICalendarEventCreator(Interface):
    """ICalendarEventCreator."""

    def getEventType():
        """ Get the calendar event type name to be adden when
            user clicks in calendar.

        @return: event type as string
        """

    def createEvent(title, start_date):
        """ Creates a calendar event in the given context and data.

        @return: the newly created event
        """
