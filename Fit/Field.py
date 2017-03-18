#!/usr/bin/env python

#
# copyright Tom Goetz
#

import logging

from time import time, gmtime, localtime
from datetime import tzinfo, timedelta, datetime


class FieldValue():

    def __init__(self, name, type, invalid, value, orig, units=''):
        self._value = {}

        self._value['name'] = name
        self._value['type'] = type
        self._value['value'] = value
        self._value['orig'] = orig
        self._value['invalid'] = invalid
        self._value['units'] = units

    def invalid(self):
        return (self._value['value'] == self._value['invalid'])

    def __getitem__(self, name):
        return self._value[name]

    def __iter__(self):
        return iter(self._value)

    def keys(self):
        return self._value.keys()

    def items(self):
        return self._value.items()

    def values(self):
        return self._value.values()

    def __str__(self):
        field_string = self['name'] + " " + str(self['value'])
        if self._value['units']:
            field_string += " " + self['units']
        field_string += " (" + str(self['orig']) + ")"
        if self.invalid():
            field_string += " [invalid]"
        return field_string


class Field():

    def __init__(self, name=''):
        self.name = name
        if self.__class__.__name__ == 'Field':
            self.type = 'number'
        else:
            self.type = (self.__class__.__name__)[:-len('Field')]
        if not name:
            self.name = self.type

    def convert(self, value, invalid):
        return FieldValue(self.name, self.type, invalid, value, value)


class ManufacturerField(Field):

    manufacturer = {
        1 : 'garmin',
        2 : 'garmin_fr405_antfs',
        3 : 'zephyr',
        4 : 'dayton',
        5 : 'idt',
        6 : 'srm',
        7 : 'quarq',
        8 : 'ibike',
        9 : 'saris',
        10 : 'spark_hk',
        11 : 'tanita',
        12 : 'echowell',
        13 : 'dynastream_oem',
        14 : 'nautilus',
        15 : 'dynastream',
        16 : 'timex',
        17 : 'metrigear',
        18 : 'xelic',
        19 : 'beurer',
        20 : 'cardiosport',
        21 : 'a_and_d',
        22 : 'hmm',
        23 : 'suunto',
        24 : 'thita_elektronik',
        25 : 'gpulse',
        26 : 'clean_mobile',
        27 : 'pedal_brain',
        28 : 'peaksware',
        29 : 'saxonar',
        30 : 'lemond_fitness',
        31 : 'dexcom',
        32 : 'wahoo_fitness',
        33 : 'octane_fitness',
        34 : 'archinoetics',
        35 : 'the_hurt_box',
        36 : 'citizen_systems',
        37 : 'magellan',
        38 : 'osynce',
        39 : 'holux',
        40 : 'concept2',
        42 : 'one_giant_leap',
        43 : 'ace_sensor',
        44 : 'brim_brothers',
        45 : 'xplova',
        46 : 'perception_digital',
        47 : 'bf1systems',
        48 : 'pioneer',
        49 : 'spantec',
        50 : 'metalogics',
        51 : '4iiiis',
        52 : 'seiko_epson',
        53 : 'seiko_epson_oem',
        54 : 'ifor_powell',
        55 : 'maxwell_guider',
        56 : 'star_trac',
        57 : 'breakaway',
        58 : 'alatech_technology_ltd',
        59 : 'mio_technology_europe',
        60 : 'rotor',
        61 : 'geonaute',
        62 : 'id_bike',
        63 : 'specialized',
        64 : 'wtek',
        65 : 'physical_enterprises',
        66 : 'north_pole_engineering',
        67 : 'bkool',
        68 : 'cateye',
        69 : 'stages_cycling',
        70 : 'sigmasport',
        71 : 'tomtom',
        72 : 'peripedal',
        73 : 'wattbike',
        76 : 'moxy',
        77 : 'ciclosport',
        78 : 'powerbahn',
        79 : 'acorn_projects_aps',
        80 : 'lifebeam',
        81 : 'bontrager',
        82 : 'wellgo',
        83 : 'scosche',
        84 : 'magura',
        85 : 'woodway',
        86 : 'elite',
        87 : 'nielsen_kellerman',
        88 : 'dk_city',
        89 : 'tacx',
        90 : 'direction_technology',
        91 : 'magtonic',
        92 : '1partcarbon',
        93 : 'inside_ride_technologies',
        94 : 'sound_of_motion',
        95 : 'stryd',
        96 : 'icg',
        97 : 'MiPulse',
        98 : 'bsx_athletics',
        99 : 'look',
        100 : 'campagnolo_srl',
        101 : 'body_bike_smart',
        102 : 'praxisworks',
        103 : 'limits_technology',
        104 : 'topaction_technology',
        105 : 'cosinuss',
        106 : 'fitcare',
        107 : 'magene',
        108 : 'giant_manufacturing_co',
        109 : 'tigrasport',
        110 : 'salutron',
        255 : 'development',
        257 : 'healthandlife',
        258 : 'lezyne',
        259 : 'scribe_labs',
        260 : 'zwift',
        261 : 'watteam',
        262 : 'recon',
        263 : 'favero_electronics',
        264 : 'dynovelo',
        265 : 'strava',
        266 : 'precor',
        267 : 'bryton',
        268 : 'sram',
        269 : 'navman',
        270 : 'cobi',
        271 : 'spivi',
        272 : 'mio_magellan',
        273 : 'evesports',
        274 : 'sensitivus_gauge',
        275 : 'podoon',
        276 : 'life_time_fitness',
        277 : 'falco_e_motors',
        5759 : 'actigraphcorp'
    }

    def __init__(self):
        Field.__init__(self)

    def convert(self, value, invalid):
        try:
            manufacturer = ManufacturerField.manufacturer[value]
        except:
            manufacturer = value
        return FieldValue(self.name, self.type, invalid, manufacturer, value)


class ProductField(Field):

    product = {
        1 : 'hrm1',
        2 : 'axh01',
        3 : 'axb01',
        4 : 'axb02',
        5 : 'hrm2ss',
        6 : 'dsi_alf02',
        7 : 'hrm3ss',
        8 : 'hrm_run_single_byte_product_id',
        9 : 'bsm',
        10 : 'bcm',
        11 : 'axs01',
        12 : 'hrm_tri_single_byte_product_id',
        14 : 'fr225_single_byte_product_id',
        473 : 'fr301_china',
        474 : 'fr301_japan',
        475 : 'fr301_korea',
        494 : 'fr301_taiwan',
        717 : 'fr405',
        782 : 'fr50',
        987 : 'fr405_japan',
        988 : 'fr60',
        1011 : 'dsi_alf01',
        1018 : 'fr310xt',
        1036 : 'edge500',
        1124 : 'fr110',
        1169 : 'edge800',
        1199 : 'edge500_taiwan',
        1213 : 'edge500_japan',
        1253 : 'chirp',
        1274 : 'fr110_japan',
        1325 : 'edge200',
        1328 : 'fr910xt',
        1333 : 'edge800_taiwan',
        1334 : 'edge800_japan',
        1341 : 'alf04',
        1345 : 'fr610',
        1360 : 'fr210_japan',
        1380 : 'vector_ss',
        1381 : 'vector_cp',
        1386 : 'edge800_china',
        1387 : 'edge500_china',
        1410 : 'fr610_japan',
        1422 : 'edge500_korea',
        1436 : 'fr70',
        1446 : 'fr310xt_4t',
        1461 : 'amx',
        1482 : 'fr10',
        1497 : 'edge800_korea',
        1499 : 'swim',
        1537 : 'fr910xt_china',
        1551 : 'fenix',
        1555 : 'edge200_taiwan',
        1561 : 'edge510',
        1567 : 'edge810',
        1570 : 'tempe',
        1600 : 'fr910xt_japan',
        1623 : 'fr620',
        1632 : 'fr220',
        1664 : 'fr910xt_korea',
        1688 : 'fr10_japan',
        1721 : 'edge810_japan',
        1735 : 'virb_elite',
        1736 : 'edge_touring',
        1742 : 'edge510_japan',
        1743 : 'hrm_tri',
        1752 : 'hrm_run',
        1765 : 'fr920xt',
        1821 : 'edge510_asia',
        1822 : 'edge810_china',
        1823 : 'edge810_taiwan',
        1836 : 'edge1000',
        1837 : 'vivo_fit',
        1853 : 'virb_remote',
        1885 : 'vivo_ki',
        1903 : 'fr15',
        1907 : 'vivo_active',
        1918 : 'edge510_korea',
        1928 : 'fr620_japan',
        1929 : 'fr620_china',
        1930 : 'fr220_japan',
        1931 : 'fr220_china',
        1936 : 'approach_s6',
        1956 : 'vivo_smart',
        1967 : 'fenix2',
        1988 : 'epix',
        2050 : 'fenix3',
        2052 : 'edge1000_taiwan',
        2053 : 'edge1000_japan',
        2061 : 'fr15_japan',
        2067 : 'edge520',
        2070 : 'edge1000_china',
        2072 : 'fr620_russia',
        2073 : 'fr220_russia',
        2079 : 'vector_s',
        2100 : 'edge1000_korea',
        2130 : 'fr920xt_taiwan',
        2131 : 'fr920xt_china',
        2132 : 'fr920xt_japan',
        2134 : 'virbx',
        2135 : 'vivo_smart_apac',
        2140 : 'etrex_touch',
        2147 : 'edge25',
        2148 : 'fr25',
        2150 : 'vivo_fit2',
        2153 : 'fr225',
        2156 : 'fr630',
        2157 : 'fr230',
        2160 : 'vivo_active_apac',
        2161 : 'vector_2',
        2162 : 'vector_2s',
        2172 : 'virbxe',
        2173 : 'fr620_taiwan',
        2174 : 'fr220_taiwan',
        2175 : 'truswing',
        2188 : 'fenix3_china',
        2189 : 'fenix3_twn',
        2192 : 'varia_headlight',
        2193 : 'varia_taillight_old',
        2204 : 'edge_explore_1000',
        2219 : 'fr225_asia',
        2225 : 'varia_radar_taillight',
        2226 : 'varia_radar_display',
        2238 : 'edge20',
        2262 : 'd2_bravo',
        2266 : 'approach_s20',
        2276 : 'varia_remote',
        2327 : 'hrm4_run',
        2337 : 'vivo_active_hr',
        2347 : 'vivo_smart_gps_hr',
        2348 : 'vivo_smart_hr',
        2368 : 'vivo_move',
        2398 : 'varia_vision',
        2406 : 'vivo_fit3',
        2413 : 'fenix3_hr',
        2429 : 'index_smart_scale',
        2431 : 'fr235',
        2441 : 'oregon7xx',
        2444 : 'rino7xx',
        2496 : 'nautix',
        2530 : 'edge_820',
        2531 : 'edge_explore_820',
        10007 : 'sdm4',
        10014 : 'edge_remote',
        20119 : 'training_center',
        65531 : 'connectiq_simulator',
        65532 : 'android_antplus_plugin',
        65534 : 'connect'
    }

    def __init__(self, name):
        Field.__init__(self, name)

    def convert(self, value, invalid):
        try:
            product = ProductField.product[value]
        except:
            product = value
        return FieldValue(self.name, self.type, invalid, product, value)


class BatteryVoltageField(Field):
    def __init__(self):
        Field.__init__(self)

    def convert(self, value, invalid):
        return FieldValue( self.name, self.type, invalid, value / 256.0, value, 'v')


class GenderField(Field):

    gender = { 0 : 'female', 1 : 'male' }

    def __init__(self):
        Field.__init__(self)

    def convert(self, value):
        return FieldValue(self.name, self.type, GenderField.gender[value], value)


class HeightField(Field):
    def __init__(self):
        Field.__init__(self)

    def convert(self, value, invalid):
        return FieldValue( self.name, self.type, invalid, value / 100.0, value, 'm')


class WeightField(Field):
    def __init__(self):
        Field.__init__(self)

    def convert(self, value, invalid):
        return FieldValue( self.name, self.type, invalid, value / 100.0, value, 'kg')


class HeartRateField(Field):
    def __init__(self, name):
        Field.__init__(self, name)

    def convert(self, value, invalid):
        return FieldValue( self.name, self.type, invalid, value, value, 'bpm')


class TimestampField(Field):

    def __init__(self, name='timestamp', utc=True):
        self.utc = utc
        Field.__init__(self, name)

    def convert(self, value, invalid):
        if self.utc:
            timestamp = time()
            time_now = datetime.fromtimestamp(timestamp)
            time_utc = datetime.utcfromtimestamp(timestamp)
            utc_offset_secs = (time_now - time_utc).total_seconds()
            value += utc_offset_secs
        timestamp = datetime(1989, 12, 31, 0, 0, 0) +  timedelta(0, value)
        return FieldValue( self.name, self.type, invalid, timestamp.isoformat(), value)


class TimeField(Field):

    def __init__(self, name):
        Field.__init__(self, name)

    def convert(self, value, invalid):
        return FieldValue(self.name, self.type, invalid, value / 1000.0, value, 's')


class DistanceField(Field):

    def __init__(self, name):
        Field.__init__(self, name)

    def convert(self, value, invalid):
        return FieldValue(self.name, self.type, invalid, value / 100.0, value, 'm')


class PercentField(Field):

    def __init__(self, name):
        Field.__init__(self, name='name')

    def convert(self, value, invalid):
        return FieldValue(self.name, self.type, invalid, value / 100.0, value, '%')


class StringField(Field):

    def __init__(self, name):
        Field.__init__(self, name)

    def convert(self, value, invalid):
        return FieldValue(self.name, self.type, invalid, str(value), value)


class UnknownField(Field):

    def __init__(self):
        Field.__init__(self)

    def convert(self, value, invalid):
        return FieldValue(self.name, self.type, invalid, value, value)


class FileField(Field):

    file_types = { 1 : 'device', 2 : 'settings', 3 : 'sport', 4 : 'activity', 5 : 'workout', 6 : 'course', 7 : 'schedules',
                    9 : 'weight', 10 : 'totals', 11 : 'goals', 14 : 'blood_pressure', 15 : 'monitoring_a', 20 : 'activity_summary',
                    28 : 'monitoring_daily', 32 : 'monitoring_b', 34 : 'segment', 35 : 'segment_list', 40 : 'exd_configuration' }

    def __init__(self, name):
        Field.__init__(self, name)

    def convert(self, value, invalid):
        return FieldValue(self.name, self.type, invalid, FileField.file_types[value], value)


class VersionField(Field):

    def __init__(self, name):
        Field.__init__(self, name)

    def convert(self, value, invalid, ):
        return FieldValue(self.name, self.type, invalid, value / 100.0, value)


class EventField(Field):

    event = { 0 : 'timer', 3 : 'workout', 4 : 'workout_step', 5 : 'power_down', 6 : 'power_up', 7 : 'off_course', 8 : 'session',
              9 : 'lap', 10 : 'course_point', 11 : 'battery', 12 : 'virtual_partner_pace', 13 : 'hr_high_alert', 14 : 'hr_low_alert',
              15 : 'speed_high_alert', 16 : 'speed_low_alert', 17 : 'cad_high_alert', 18 : 'cad_low_alert', 19 : 'power_high_alert',
              20 : 'power_low_alert', 21 : 'recovery_hr', 22 : 'battery_low', 23 : 'time_duration_alert', 24 : 'distance_duration_alert',
              25 : 'calorie_duration_alert', 26 : 'activity', 27 : 'fitness_equipment', 28 : 'length', 32 : 'user_marker',
              33 : 'sport_point', 36 : 'calibration', 41 : 'unknown', 42 : 'front_gear_change', 43 : 'rear_gear_change',
              44 : 'rider_position_change', 45 : 'elev_high_alert', 46 : 'elev_low_alert', 47 : 'comm_timeout' }

    def __init__(self):
        Field.__init__(self)

    def convert(self, value, invalid):
        try:
            newvalue = EventField.event[value]
        except:
            newvalue = value
        return FieldValue(self.name, self.type, invalid, newvalue, value)


class EventTypeField(Field):

    type = { 0 : 'start', 1 : 'stop', 2 : 'consecutive_depreciated', 3 : 'marker', 4 : 'stop_all', 5 : 'begin_depreciated',
                   6 : 'end_depreciated', 7 : 'end_all_depreciated', 8 : 'stop_disable', 9 : 'stop_disable_all'}

    def __init__(self):
        Field.__init__(self)

    def convert(self, value, invalid):
        try:
            newvalue = EventTypeField.type[value]
        except:
            newvalue = value
        return FieldValue(self.name, self.type, invalid, newvalue, value)


class ActivityField(Field):

    type = { 0 : 'manual', 1 : 'auto_multi_sport' }

    def __init__(self):
        Field.__init__(self)

    def convert(self, value, invalid):
        try:
            newvalue = ActivityField.type[value]
        except:
            newvalue = value
        return FieldValue(self.name, self.type, invalid, newvalue, value)


class ActivityTypeField(Field):

    type = { 0 : 'generic', 1 : 'running', 2 : 'cycling', 3 : 'transition', 4 : 'fitness_equipment', 5 : 'swimming',
                   6 : 'walking', 7 : 'sedentary', 8 : 'stop_disable', 245 : 'all'}

    def __init__(self):
        Field.__init__(self)

    def convert(self, value, invalid):
        converted_value = ''
        if isinstance(value, list):
            for sub_value in value:
                converted_value += ActivityTypeField.type[sub_value] + " "
        else:
            converted_value = ActivityTypeField.type[value]
        return FieldValue(self.name, self.type, invalid, converted_value, value)


class LapTriggerField(Field):

    type = { 0 : 'manual', 1 : 'time', 2 : 'distance', 3 : 'position_start', 4 : 'position_lap', 5 : 'position_waypoint',
             6 : 'position_marked', 7 : 'session_end', 8 : 'fitness_equipment' }

    def __init__(self):
        Field.__init__(self)

    def convert(self, value, invalid):
        try:
            newvalue = LapTriggerField.type[value]
        except:
            newvalue = value
        return FieldValue(self.name, self.type, invalid, newvalue, value)


class SessionTriggerField(Field):

    type = { 0 : 'activity_end', 1 : 'manual', 2 : 'auto_multi_sport', 3 : 'fitness_equipment' }

    def __init__(self):
        Field.__init__(self)

    def convert(self, value, invalid):
        try:
            newvalue = SessionTriggerField.type[value]
        except:
            newvalue = value
        return FieldValue(self.name, self.type, invalid, newvalue, value)


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
        Field.__init__(self)

    def convert(self, value, invalid):
        try:
            newvalue = SportField.type[value]
        except:
            newvalue = value
        return FieldValue(self.name, self.type, invalid, newvalue, value)


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
        Field.__init__(self)

    def convert(self, value, invalid):
        try:
            newvalue = SubSportField.type[value]
        except:
            newvalue = value
        return FieldValue(self.name, self.type, invalid, newvalue, value)

class PosField(Field):

    def __init__(self, name):
        Field.__init__(self, name)

    def convert(self, value, invalid):
        return FieldValue(self.name, self.type, invalid, value, value, 'semicircles')


class AltField(Field):

    def __init__(self, name):
        Field.__init__(self, name)

    def convert(self, value, invalid):
        return FieldValue(self.name, self.type, invalid, value, value, 'm')


