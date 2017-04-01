#!/usr/bin/env python

#
# copyright Tom Goetz
#

import logging
from datetime import tzinfo, timedelta, datetime

from OutputData import OutputData
from FieldStats import *


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MonitoringOutputData(OutputData):
    track_max = [ 'cum_active_time' ]
    def __init__(self, files):
        self.heading_names_list = ['timestamp', 'activity_type'] 
        self.field_names_list = ['timestamp', 'activity_type'] 

        self.monitoring_info = []

        self._day_stats = {}
        self._stats_headings = FieldStats.stat_names

        self.last_timestamp_16 = 0
        self.matched_timestamp_16 = 0

        OutputData.__init__(self, files)

    def parse_info(self, file):
        monitoring_info_messages = file['monitoring_info']
        if monitoring_info_messages:
            monitoring_info_msg = monitoring_info_messages[0]
            self.local_timestamp = monitoring_info_msg['local_timestamp']['value']
            self.last_timestamp = self.local_timestamp
            activity_type = monitoring_info_msg['activity_type']['value']
            resting_metabolic_rate = monitoring_info_msg['resting_metabolic_rate']['value']
            cycles_to_distance = monitoring_info_msg['cycles_to_distance']['value']
            cycles_to_calories = monitoring_info_msg['cycles_to_calories']['value']
            monitoring_info_entry = {
                'file'                      : file.filename,
                'local_timestamp'           : self.local_timestamp,
                'activity_type'             : activity_type,
                'resting_metabolic_rate'    : resting_metabolic_rate,
                'cycles_to_distance'        : cycles_to_distance,
                'cycles_to_calories'        : cycles_to_calories
            }
            self.monitoring_info.append(monitoring_info_entry)

    def add_entry_field(self, entry, field_name, field_value, units=None):
        entry[field_name] = field_value

        if not field_name in self.field_names_list:
            logger.debug(field_name + ": " + str(units))
            self.field_names_list.append(field_name)
            if units:
                heading = field_name + " (" + units + ")"
            else:
                heading = field_name
            self.heading_names_list.append(heading)

    def parse_message(self, message, day):
        entry = {}
        for field_name in message:
            field = message[field_name]

            if field_name == 'timestamp' or field_name == 'timestamp_16':
                self.add_entry_field(entry, 'timestamp', message.timestamp())
            else:
                self.add_entry_field(entry, field_name, field['value'], field.units())
                self._day_stats[day].accumulate(field_name, field)

        logger.debug(message.name() + ": " + str(entry))

        return entry

    def parse_messages(self, file):
        self.parse_info(file)

        day_created = self.local_timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        if not day_created in self._day_stats.keys():
            self._day_stats[day_created] = DayStats()

        monitoring_messages = file['monitoring']
        if monitoring_messages:
            for message in monitoring_messages:
                self.entries.append(self.parse_message(message, day_created))

        self.entries.sort(key=lambda item:item['timestamp'])

    def get_info(self):
        return self.monitoring_info

    def field_names(self):
        return self.field_names_list

    def heading_names(self):
        return self.heading_names_list

    def add_derived_stats(self, stats_day):
        derived_stats = {
            'total_steps' : ['walking_steps', 'running_steps'],
            'total_floors' : ['cum_ascent_floors']
        }
        for derived_stat in derived_stats:
            component_stat_names = derived_stats[derived_stat]
            stat = { 'count' : 0, 'max' : 0, 'avg' : 0, 'total' : 0, 'min' : 0 }
            for component_stat_name in component_stat_names:
                if component_stat_name in stats_day.keys():
                    component_stat = stats_day[component_stat_name]
                    stat['count'] += component_stat['count']
                    stat['max'] = 0
                    stat['avg'] = 0
                    stat['total'] += int(component_stat['max'])
                    stat['min'] = 0
            stats_day[derived_stat] = stat

    def get_stats_headings(self):
        return self._stats_headings

    def get_day_stats(self):
        stats = {}
        days = self._day_stats.keys()
        for day in days:
            stats[day] = {}
            day_stats = self._day_stats[day]
            for field_name in day_stats.keys():
                field_stats = day_stats[field_name]
                field_stats_values = field_stats.get()
                if field_stats_values:
                    stats[day][field_name] = field_stats_values
            self.add_derived_stats(stats[day])
        return stats
