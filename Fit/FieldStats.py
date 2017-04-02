#!/usr/bin/env python

#
# copyright Tom Goetz
#

import sys

from FieldValue import FieldValue


class FieldStats():
    stats_none          = 0x0000
    stats_max           = 0x0001
    stats_min           = 0x0002
    stats_avg           = 0x0004
    stats_tot           = 0x0008
    stats_cum           = 0x0010
    stats_commulative = (stats_max | stats_min | stats_cum)
    stats_all = (stats_max | stats_min | stats_avg | stats_tot)

    stat_names = ['count', 'max', 'avg', 'total', 'min']

    def __init__(self, mode):
        self._mode = mode
        self.clear()

    def clear(self):
        self._stats = {}
        self._stats['count'] = 0
        self._stats['max'] = 0
        self._stats['avg'] = 0
        self._stats['total'] = 0
        self._stats['min'] = sys.maxint

    def accumulate(self, value):
        self._stats['count'] += 1
        if value > self._stats['max']:
            self._stats['max'] = value
        if value and value < self._stats['min']:
            self._stats['min'] = value
        self._stats['total'] += value
        self._stats['avg'] = self._stats['total'] / self._stats['count']

    def get(self):
        if not self._stats['count'] or not self._mode:
            return None
        stats = self._stats.copy()
        self.clear()
        if not (self._mode & FieldStats.stats_max):
            stats['max'] = 0
        if not (self._mode & FieldStats.stats_min):
            stats['min'] = 0
        if not (self._mode & FieldStats.stats_avg):
            stats['avg'] = 0
        if not (self._mode & FieldStats.stats_tot):
            stats['total'] = 0
        return stats

    def __str__(self):
        return ("%s: %s" % (self.__class__.__name__, str(self._stats)))

    def __repr__(self):
        return self.__str__()


class DayStats():
    def __init__(self):
        self._field_stats = {}

    def accumulate(self, name, field_value):
        stats_mode = field_value.field._stats_mode
        if stats_mode:
            if not name in self._field_stats.keys():
                self._field_stats[name] = FieldStats(stats_mode)
            self._field_stats[name].accumulate(field_value.value())

    def __getitem__(self, name):
        return self._field_stats[name]

    def __iter__(self):
        return iter(self._field_stats)

    def keys(self):
        return self._field_stats.keys()

    def items(self):
        return self._field_stats.items()

    def values(self):
        return self._field_stats.values()

    def __str__(self):
        return ("%s" % (self.__class__.__name__))

    def __repr__(self):
        return self.__str__()