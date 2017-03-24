#!/usr/bin/env python

#
# copyright Tom Goetz
#

import sys, logging, collections, traceback
from datetime import tzinfo, timedelta, datetime

from FileHeader import FileHeader
from RecordHeader import RecordHeader
from DefinitionMessage import DefinitionMessage
from DataMessage import DataMessage
from MonitoringOutputData import MonitoringOutputData
from DeviceOutputData import DeviceOutputData


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class FitParseError(Exception):
    def __init__(self, message):
        self.message = message
        self.tb = traceback.format_exc()

    def __str__(self):
        return repr(self.message + ": " + self.tb)


class File():

    def __init__(self, filename, english_units=False):
        self.filename = filename
        self.english_units = english_units

        self.last_date = None
        self.last_day = None

        self.last_timestamp_16 = 0
        self.matched_timestamp_16 = 0

        self.file = open(filename, 'rb')
        try:
            self.parse()
        except IndexError as error:
            raise FitParseError(str(error) + " in " + filename)

    def add_message_stats(self, message):
        timestamp = entry['timestamp']
        date = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        if date != self.last_date:
            self._days[date] = self._stats.copy()
            self.last_date = date
        self.last_entry = entry

    def timestamp16_to_timestamp(self, timestamp_16):
        self.last_timestamp_16 = timestamp_16
        delta = timestamp_16 - self.matched_timestamp_16
        return self.last_message_timestamp + timedelta(0, delta)

    def record_day_stats(self):
        stats = {}
        for field_name in self._stats.keys():
            field_stats_obj = self._stats[field_name]
            field_stats = field_stats_obj.get()
            if field_stats and field_stats['count'] > 0:
                stats[field_name] = field_stats
        self._days[self.last_day] = stats

    def track_dates(self, timestamp):
        day = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        if self.last_day and day != self.last_day:
            self.record_day_stats()
        self.last_day = day

        self.last_message_timestamp = timestamp
        self.matched_timestamp_16 = self.last_timestamp_16

    def capture_stats(self, message):
        for field_name in message:
            field = message[field_name]
            field_stats_obj = field.stats()
            if field_stats_obj:
                self._stats[field_name] = field_stats_obj

    def parse(self):
        self.file_header = FileHeader(self.file)
        if not self.file_header.check():
            logger.error("Bad header: " + str(self.file_header))
            return False

        self.data_size = self.file_header.get_data_size()

        self._definition_messages = {}
        self._data_messages = {}
        self._stats = {}
        self._days = {}
        data_consumed = 0
        self.record_count = 0
        self.first_message_timestamp = None
        self.last_message_timestamp = None

        while self.data_size > data_consumed:
            record_header = RecordHeader(self.file)
            local_message_num = record_header.local_message()
            data_consumed += record_header.file_size
            self.record_count += 1

            if record_header.definition_message():
                definition_message = DefinitionMessage(record_header, self.file)
                data_consumed += definition_message.file_size
                self._definition_messages[local_message_num] = definition_message

            elif record_header.data_message():
                definition_message = self._definition_messages[local_message_num]
                try:
                    data_message = DataMessage(definition_message, self.file, self.english_units)
                except:
                    raise FitParseError("Failed to parse " + definition_message.name())

                self.capture_stats(data_message)
                data_consumed += data_message.file_size

                data_message_name = data_message.name()

                time_created_timestamp = data_message['time_created']
                if time_created_timestamp:
                    self.time_created_timestamp = time_created_timestamp['value']

                message_timestamp = data_message['timestamp']
                if message_timestamp:
                    message_timestamp_value = message_timestamp['value']
                    self.track_dates(message_timestamp_value)
                else:
                    message_timestamp_16 = data_message['timestamp_16']
                    if message_timestamp_16:
                        message_timestamp_16_value = message_timestamp_16['value']
                        message_timestamp_value = self.timestamp16_to_timestamp(message_timestamp_16_value)
                    else:
                        message_timestamp_value = self.last_message_timestamp
                data_message._timestamp = message_timestamp_value

                try:
                    self._data_messages[data_message_name].append(data_message)
                except:
                    self._data_messages[data_message_name] = [ data_message ]

            logger.debug("Record %d: consumed %d of %s %r" %
                            (self.record_count, data_consumed, self.data_size, self.english_units))

        self.record_day_stats()

    def type(self):
        return self['file_id'][0]['type']

    def time_created(self):
        return self['file_id'][0]['time_created']

    def date_span(self):
        return (self.time_created_timestamp, self.last_message_timestamp)

    def get_summary(self):
        return self._days

    def get_summary_headings(self):
        first_day = self._days.itervalues().next()
        if first_day:
            first_field = first_day.itervalues().next()
            return first_field.keys()
        return None

    def get_device(self):
        return DeviceOutputData(self)

    def __getitem__(self, name):
        return self._data_messages[name]


