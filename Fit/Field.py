#!/usr/bin/env python

#
# copyright Tom Goetz
#

import logging

from time import time, gmtime, localtime
from datetime import tzinfo, timedelta, datetime


class Field():

    def __init__(self, name, type='number'):
        self.name = name
        self.type = type

    def convert(self, value):
        return value

    def display(self, value):
        if self.name != self.type:
            return (self.name + " (" + self.type + ") " + str(self.convert(value)))
        return (self.name + " : " + str(self.convert(value)))

    def __str__(self):
        return (self.__class__.__name__ + " : " + self.name)


class ManufacturerField(Field):

    manufacturer = { 1 : 'Garmin' }

    def __init__(self, name):
        Field.__init__(self, name, 'manufacturer')

    def convert(self, value):
        return ManufacturerField.manufacturer[value];


class ProductField(Field):

    product = { 2337 : 'VivoActive HR' }

    def __init__(self, name):
        Field.__init__(self, name, 'product')

    def convert(self, value):
        return ProductField.product[value];


class TimestampField(Field):

    def __init__(self, name='timestamp', utc=True):
        self.utc = utc
        Field.__init__(self, name, 'date_time')

    def convert(self, value):
        if self.utc:
            timestamp = time()
            time_now = datetime.fromtimestamp(timestamp)
            time_utc = datetime.utcfromtimestamp(timestamp)
            utc_offset_secs = (time_now - time_utc).total_seconds()
            value += utc_offset_secs
        timestamp = datetime(1989, 12, 31, 0, 0, 0) +  timedelta(0, value)
        return timestamp.isoformat();


class StringField(Field):

    def __init__(self, name):
        Field.__init__(self, name, 'string')

    def convert(self, value):
        return value


class UnknownField(Field):

    def __init__(self):
        Field.__init__(self, 'unknown')


class FileField(Field):

    file_types = { 1 : 'device', 2 : 'settings', 3 : 'sport', 4 : 'activity', 5 : 'workout', 6 : 'course', 7 : 'schedules',
                    9 : 'weight', 10 : 'totals', 11 : 'goals', 14 : 'blood_pressure', 15 : 'monitoring_a', 20 : 'activity_summary',
                    28 : 'monitoring_daily', 32 : 'monitoring_b', 34 : 'segment', 35 : 'segment_list', 40 : 'exd_configuration' }

    def __init__(self, name):
        Field.__init__(self, name, 'file')

    def convert(self, value):
        return FileField.file_types[value]


class VersionField(Field):

    def __init__(self, name):
        Field.__init__(self, name, 'version')

    def convert(self, value):
        return (value)


class EventField(Field):

    event = { 0 : 'timer', 3 : 'workout', 4 : 'workout_step', 5 : 'power_down', 6 : 'power_up', 7 : 'off_course', 8 : 'session',
              9 : 'lap', 10 : 'course_point', 11 : 'battery', 12 : 'virtual_partner_pace', 13 : 'hr_high_alert', 14 : 'hr_low_alert',
              15 : 'speed_high_alert', 16 : 'speed_low_alert', 17 : 'cad_high_alert', 18 : 'cad_low_alert', 19 : 'power_high_alert',
              20 : 'power_low_alert', 21 : 'recovery_hr', 22 : 'battery_low', 23 : 'time_duration_alert', 24 : 'distance_duration_alert',
              25 : 'calorie_duration_alert', 26 : 'activity', 27 : 'fitness_equipment', 28 : 'length', 32 : 'user_marker',
              33 : 'sport_point', 36 : 'calibration', 41 : 'unknown', 42 : 'front_gear_change', 43 : 'rear_gear_change',
              44 : 'rider_position_change', 45 : 'elev_high_alert', 46 : 'elev_low_alert', 47 : 'comm_timeout', 54 : 'unknown' }

    def __init__(self):
        Field.__init__(self, 'event', 'event')

    def convert(self, value):
        return EventField.event[value]


class EventTypeField(Field):

    type = { 0 : 'start', 1 : 'stop', 2 : 'consecutive_depreciated', 3 : 'marker', 4 : 'stop_all', 5 : 'begin_depreciated',
                   6 : 'end_depreciated', 7 : 'end_all_depreciated', 8 : 'stop_disable', 9 : 'stop_disable_all'}

    def __init__(self):
        Field.__init__(self, 'event_type', 'event_type')

    def convert(self, value):
        return EventTypeField.type[value]


class ActivityTypeField(Field):

    type = { 0 : 'generic', 1 : 'running', 2 : 'cycling', 3 : 'transition', 4 : 'fitness_equipment', 5 : 'swimming',
                   6 : 'walking', 8 : 'sedentary', 8 : 'stop_disable', 245 : 'all'}

    def __init__(self):
        Field.__init__(self, 'activity_type', 'activity_type')

    def convert(self, value):
        converted_value = ''
        if isinstance(value, list):
            for sub_value in value:
                converted_value += ActivityTypeField.type[sub_value] + " "
        else:
            converted_value = ActivityTypeField.type[value]
        return converted_value


