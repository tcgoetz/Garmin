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

    manufacturer = { 1 : 'Garmin', 15 : 'dynastream' }

    def __init__(self, name):
        Field.__init__(self, name, 'manufacturer')

    def convert(self, value):
        return ManufacturerField.manufacturer[value];


class ProductField(Field):

    product = { 1 : 'hrm1', 2337 : 'VivoActive HR' }

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


class TimeField(Field):

    def __init__(self, name):
        Field.__init__(self, name, 'time')

    def convert(self, value):
        return value / 1000


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


class ActivityField(Field):

    type = { 0 : 'manual', 1 : 'auto_multi_sport' }

    def __init__(self):
        Field.__init__(self, 'type', 'type')

    def convert(self, value):
        return ActivityField.type[value]


class ActivityTypeField(Field):

    type = { 0 : 'generic', 1 : 'running', 2 : 'cycling', 3 : 'transition', 4 : 'fitness_equipment', 5 : 'swimming',
                   6 : 'walking', 7 : 'sedentary', 8 : 'stop_disable', 245 : 'all'}

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


class LapTriggerField(Field):

    type = { 0 : 'manual', 1 : 'time', 2 : 'distance', 3 : 'position_start', 4 : 'position_lap', 5 : 'position_waypoint',
             6 : 'position_marked', 7 : 'session_end', 8 : 'fitness_equipment' }

    def __init__(self):
        Field.__init__(self, 'lap_trigger', 'lap_trigger')

    def convert(self, value):
        return LapTriggerField.type[value]


class SessionTriggerField(Field):

    type = { 0 : 'activity_end', 1 : 'manual', 2 : 'auto_multi_sport', 3 : 'fitness_equipment' }

    def __init__(self):
        Field.__init__(self, 'session_trigger', 'session_trigger')

    def convert(self, value):
        return SessionTriggerField.type[value]


class SportField(Field):

    type = { 
        0 : 'generic', 1 : 'running', 2 : 'cycling', 3 : 'transition', 4 : 'fitness_equipment', 5 : 'swimming',
        6 : 'basketball', 7 : 'soccer', 8 : 'tennis', 9 : 'american_football', 10 : 'training', 11 : 'walking',
        12 : 'cross_country_skiing', 13 : 'alpine_skiing', 14 : 'snowboarding', 15 : 'rowing', 16 : 'mountaineering', 17 : 'hiking', 
        18 : 'multisport', 19 : 'paddling', 20 : 'flying', 21 : 'e_biking', 22 : 'motorcycling', 23 : 'boating', 24 : 'driving',
        25 : 'golf', 26 : 'hang_gliding', 27 : 'horseback_riding', 28 : 'hunting', 29 : 'fishing', 30 : 'inline_skating', 31 : 'rock_climbing',
        32 : 'sailing', 33 : 'ice_skating', 34 : 'sky_diving', 35 : 'snowshoeing', 36 : 'snowmobiling', 37 : 'stand_up_paddleboarding', 38 : 'surfing',
        39 : 'wakeboarding', 40 : 'water_skiing', 41 : 'kayaking', 42 : 'rafting', 43 : 'windsurfing', 44 : 'kitesurfing', 45 : 'tactical',
        46 : 'jumpmaster', 47 : 'boxing', 48 : 'floor_climbing'
    }

    def __init__(self):
        Field.__init__(self, 'sport', 'sport')

    def convert(self, value):
        return SportField.type[value]


class SubSportField(Field):

    type = { 
        0 : 'generic', 1 : 'treadmill', 2 : 'street', 3 : 'trail', 4 : 'track', 5 : 'spiin',
        6 : 'indoor_cycling', 7 : 'road', 8 : 'mountain', 9 : 'downhill', 10 : 'recumbent', 11 : 'cyclocross',
        12 : 'hand_cycling', 13 : 'track_cycling', 14 : 'indoor_rowing', 15 : 'elliptical', 16 : 'stair_climbing', 17 : 'lap_swimming', 
        18 : 'open_water', 19 : 'flexibility_training', 20 : 'strength_training', 21 : 'warm_up', 22 : 'match', 23 : 'exercise', 24 : 'challenge',
        25 : 'indoor_skiing', 26 : 'cardio_training', 27 : 'indoor_walking', 28 : 'e_bike_fitness', 29 : 'bmx', 30 : 'casual_walking', 31 : 'speed_walking',
        32 : 'bike_to_run_transition', 33 : 'run_to_bike_transition', 34 : 'swim_to_bike_transition', 35 : 'atv', 36 : 'motocross', 37 : 'backcountry', 38 : 'resort',
        39 : 'rc_drone', 40 : 'wingsuit', 41 : 'whitewater', 42 : 'skate_skiing', 43 : 'yoga', 44 : 'pilates', 45 : 'indoor_running',
        46 : 'gravel_cycling', 47 : 'e_bike_mountain', 48 : 'commuting', 49 : 'mixed_surface', 50 : 'navigate', 51 : 'track_me',
        52 : 'map', 254 : 'all'
    }

    def __init__(self):
        Field.__init__(self, 'sport', 'sport')

    def convert(self, value):
        return SubSportField.type[value]


class PosField(Field):

    def __init__(self, name):
        Field.__init__(self, name, 'semicircles')

    def convert(self, value):
        return value


class AltField(Field):

    def __init__(self, name):
        Field.__init__(self, name, 'alt')

    def convert(self, value):
        return value


