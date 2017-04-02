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
        self._device_stats = {}
        self._overall_stats = {}
        self._stats_headings = FieldStats.stat_names

        self.last_timestamp_16 = 0
        self.matched_timestamp_16 = 0

        OutputData.__init__(self, files)
        self.summarize_stats()

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
                'timestamp'                 : self.local_timestamp,
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

    def parse_message(self, message, dev_stats):
        entry = {}
        for field_name in message:
            field = message[field_name]

            if field_name == 'timestamp' or field_name == 'timestamp_16':
                self.add_entry_field(entry, 'timestamp', message.timestamp())
            else:
                self.add_entry_field(entry, field_name, field['value'], field.units())
                dev_stats.accumulate(field_name, field)

        logger.debug(message.name() + ": " + str(entry))

        return entry

    def parse_messages(self, file):
        self.parse_info(file)

        day = self.local_timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        if not day in self._device_stats.keys():
            self._device_stats[day] = {}
        if not file.device() in self._device_stats[day].keys():
            self._device_stats[day][file.device()] = DayStats()

        monitoring_messages = file['monitoring']
        if monitoring_messages:
            for message in monitoring_messages:
                self.entries.append(self.parse_message(message, self._device_stats[day][file.device()]))

        self.entries.sort(key=lambda item:item['timestamp'])

    def concatenate_overall_field(self, overall_field, second_field):
        new_field = first_field

        new_field['count'] = overall_field['count'] + 1

        if overall_field['min'] > second_field['min']:
            new_field['min'] = second_field['min']
        else:
            new_field['min'] = overall_field['min']

        if overall_field['max'] < second_field['max']:
            new_field['max'] = second_field['max']
        else:
            new_field['max'] = overall_field['max']
        new_field['total'] = overall_field['total'] + second_field['total']
        new_field['avg'] = new_field['total'] / new_field['count']

        return new_field

    def compute_overall_stats(self, day, stats_day):
        overall_stats_fields = [ 'total_floors', 'total_steps']
        for overall_stats_field in overall_stats_fields:
            if overall_stats_field in self._overall_stats.keys():
                self._overall_stats[overall_stats_field] = self.concatenate_fields(self._overall_stats[overall_stats_field], stats_day[overall_stats_field])
            else:
                self._overall_stats[overall_stats_field] = stats_day[overall_stats_field]
                self._overall_stats[overall_stats_field]['count'] = 1
                self._overall_stats[overall_stats_field]['avg'] = self._overall_stats[overall_stats_field]['total']

    def concatenate_fields(self, first_field, second_field):
        new_field = first_field

        new_field['count'] = first_field['count'] + second_field['count']

        if first_field['min'] > second_field['min']:
            new_field['min'] = second_field['min']
        else:
            new_field['min'] = first_field['min']

        # is this a cumulative stat?
        if first_field['total'] or second_field['total']:
            if first_field['max'] < second_field['max']:
                new_field['max'] = second_field['max']
            else:
                new_field['max'] = first_field['max']
            new_field['total'] = first_field['total'] + second_field['total']
            new_field['avg'] = new_field['total'] / new_field['count']
        else:
            new_field['max'] = first_field['max'] + second_field['max']
            new_field['total'] = 0
            new_field['avg'] = 0

        return new_field

    def concatenate_days(self, first_day, second_day):
        new_day = first_day

        for field_name in second_day:
            second_day_field = second_day[field_name]
            if field_name in first_day:
                first_day_field = first_day[field_name]
                if first_day_field['count'] == 0:
                    new_day[field_name] = second_day_field.copy()
                elif second_day_field['count'] == 0:
                    new_day[field_name] = first_day_field.copy()
                else:
                    new_day[field_name] = self.concatenate_fields(first_day_field, second_day_field)
            # field_name is not in the first day
            else:
                new_day[field_name] = second_day_field.copy()

        return new_day

    def summarize_day_stats(self, day_stats):
        sum_day_stats = {}
        for field_name in day_stats.keys():
            field_stats = day_stats[field_name]
            field_stats_values = field_stats.get()
            if field_stats_values:
                sum_day_stats[field_name] = field_stats_values
        return sum_day_stats

    def summarize_stats(self):
        days = self._device_stats.keys()
        for day in days:
            dev_day_stats = self._device_stats[day]
            for day_device in dev_day_stats.keys():
                device_stats = dev_day_stats[day_device]
                summed_device_stats = self.summarize_day_stats(device_stats)
                if day in self._day_stats.keys():
                    self._day_stats[day] = self.concatenate_days(self._day_stats[day], summed_device_stats)
                else:
                    self._day_stats[day] = summed_device_stats
            day_device_count = len(dev_day_stats.keys())
            if day_device_count > 1:
                self._day_stats[day]['devices'] = {
                    'count' : day_device_count, 'max' : 0, 'avg' : 0, 'total' : day_device_count, 'min' : 0
                }

            self.add_derived_stats(self._day_stats[day])
            self.compute_overall_stats(day, self._day_stats[day])

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
        return self._day_stats

    def get_overall_stats(self):
        return self._overall_stats
