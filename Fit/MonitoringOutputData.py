#!/usr/bin/env python

#
# copyright Tom Goetz
#

import logging
from datetime import tzinfo, timedelta, datetime

from OutputData import OutputData


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MonitoringOutputData(OutputData):
    track_max = [ 'cum_active_time' ]
    def __init__(self, files):
        self.heading_names_list = ['timestamp', 'activity_type'] 
        self.field_names_list = ['timestamp', 'activity_type'] 

        self._stats = {}

        self.last_timestamp_16 = 0
        self.matched_timestamp_16 = 0

        OutputData.__init__(self, files)
        self.parse_summaries()

    def parse_info(self, file):
        monitoring_info = file['monitoring_info'][0]

        self.local_timestamp = monitoring_info['local_timestamp']['value']
        self.last_timestamp = self.local_timestamp
        self.activity_type = monitoring_info['activity_type']
        self.resting_metabolic_rate = monitoring_info['resting_metabolic_rate']
        self.cycles_to_distance = monitoring_info['cycles_to_distance']
        self.cycles_to_calories = monitoring_info['cycles_to_calories']

    # for stats that are calculated AFTER dependent fields are rewritten
    def add_entry_stats(self, timestamp, field_name, field_value, cumulative=False):
        day = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        field_stats = {}
        field_stats['count'] = 1
        field_stats['max'] = field_value
        field_stats['min'] = field_value
        if not cumulative:
            field_stats['total'] = field_value
            field_stats['avg'] = field_value
        else:
            field_stats['total'] = 0
            field_stats['avg'] = 0
        stats = {field_name : field_stats}
        if day in self._stats.keys():
            self._stats[day] = self.concatenate_days(self._stats[day], stats)
        else:
            self._stats[day] = stats.copy()

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

    def parse_message(self, message):
        entry = {}

        for field_name in message:
            field = message[field_name]

            if field_name == 'timestamp' or field_name == 'timestamp_16':
                self.add_entry_field(entry, 'timestamp', message.timestamp())
            else:
                self.add_entry_field(entry, field_name, field['value'], field.units())

        logger.debug(message.name() + ": " + str(entry))

        return entry

    def parse_messages(self, file):
        self.parse_info(file)
        for message in file['monitoring']:
            self.entries.append(self.parse_message(message))
        self.entries.sort(key=lambda item:item['timestamp'])

        for entry in self.entries:
            timestamp = entry['timestamp'] 
            for field_name in ['walking_steps', 'running_steps']:
                if field_name in entry.keys():
                    self.add_entry_stats(timestamp, field_name, entry[field_name], True)

    def field_names(self):
        return self.field_names_list

    def heading_names(self):
        return self.heading_names_list

    def concatenate_fields(self, first_field, second_field):
        new_field = first_field

        if first_field['min'] or second_field['min']:
            if first_field['min'] > second_field['min']:
                new_field['min'] = second_field['min']
            else:
                new_field['min'] = first_field['min']
        else:
            new_field['min'] = 0

        if first_field['max'] or second_field['max']:
            if first_field['max'] < second_field['max']:
                new_field['max'] = second_field['max']
            else:
                new_field['max'] = first_field['max']
        else:
            new_field['max'] = 0

        if first_field['total'] or second_field['total']:
            new_field['total'] = first_field['total'] + second_field['total']
        else:
            new_field['total'] = 0

        new_field['count'] = first_field['count'] + second_field['count']

        if first_field['avg'] or second_field['avg']:
            new_field['avg'] = new_field['total'] / new_field['count']
        else:
            new_field['avg'] =  0

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

    def add_derived_stats(self, day):
        derived_stats = {
            'total_steps' : ['walking_steps', 'running_steps']
        }
        for derived_stat in derived_stats:
            component_stat_names = derived_stats[derived_stat]
            stat = {}
            stat['count'] = 0
            stat['total'] = 0
            stat['max'] = 0
            for component_stat_name in component_stat_names:
                if component_stat_name in day.keys():
                    component_stat = day[component_stat_name]
                    stat['count'] += component_stat['count']
                    stat['total'] += component_stat['total']
                    if component_stat['max'] > stat['max']:
                        stat['max'] = component_stat['max']
            day[derived_stat] = stat

    def parse_summaries(self):
        self.summary_headings = None
        self.summary_days = {}

        for file in self.files:
            if not self.summary_headings:
                self.summary_headings = file.get_summary_headings()
            new_days = file.get_summary()
            for date in new_days:
                if date in self.summary_days:
                    self.summary_days[date] = self.concatenate_days(self.summary_days[date], new_days[date])
                else:
                    self.summary_days[date] = new_days[date].copy()

        new_days = self._stats
        for date in new_days:
            if date in self.summary_days:
                self.summary_days[date] = self.concatenate_days(self.summary_days[date], new_days[date])
            else:
                self.summary_days[date] = new_days[date].copy()

        for date in self.summary_days:
            self.add_derived_stats(self.summary_days[date])

    def get_summary_headings(self):
        return self.summary_headings

    def get_summary(self):
        return self.summary_days
