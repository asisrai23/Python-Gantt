#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gantt.py - version and date, see below

This is a python class to create gantt chart using SVG


Author : Alexandre Norman - norman at xael.org
Licence : GPL v3 or any later version


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""



__author__ = 'Alexandre Norman (norman at xael.org)'
__version__ = '0.3.1'
__last_modification__ = '2015.01.10'

import datetime
import logging
import sys

# https://bitbucket.org/mozman/svgwrite
# http://svgwrite.readthedocs.org/en/latest/

try:
    import svgwrite
    from svgwrite import cm, mm   
except ImportError:
    print("This program uses svgwrite. See : https://bitbucket.org/mozman/svgwrite/")
    sys.exit(1)


############################################################################

__LOG__ = None

############################################################################

# Unworked days (0: Monday ... 6: Sunday)
NOT_WORKED_DAYS = [5, 6]

# list of vacations as datetime (non worked days)
VACATIONS = []

############################################################################


def add_vacations(start_date, end_date=None):
    """
    Add vacations to a resource begining at [start_date] to [end_date]
    (included). If [end_date] is not defined, vacation will be for [start_date]
    day only

    Keyword arguments:
    start_date -- datetime.date begining of vacation
    end_date -- datetime.date end of vacation of vacation
    """
    __LOG__.debug('** add_vacations {0}'.format({'start_date':start_date, 'end_date':end_date}))

    global VACATIONS
    
    if end_date is None:
        if start_date not in VACATIONS:
            VACATIONS.append(start_date)
    else:
        while start_date <= end_date:
            if start_date not in VACATIONS:
                VACATIONS.append(start_date)
                
            start_date += datetime.timedelta(days=1)

    __LOG__.debug('** add_vacations {0}'.format({'start_date':start_date, 'end_date':end_date, 'vac':VACATIONS}))

    return

############################################################################

def init_log_to_sysout(level=logging.INFO):
    """
    debugging facilities
    """
    global __LOG__
    logger = logging.getLogger("Gantt")
    logger.setLevel(level)
    fh = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    __LOG__ = logging.getLogger("Gantt")
    return

############################################################################

def _show_version(name, **kwargs):
    """
    Show version
    """
    import os
    print("{0} version {1}".format(os.path.basename(name), __version__))
    return True


############################################################################


def _flatten(l, ltypes=(list, tuple)):
    """
    Return a flatten list from a list like [1,2,[4,5,1]]
    """
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)

############################################################################
class GroupOfResources(object):
    """
    Class for grouping resources
    """
    def __init__(self, name, fullname=None):
        """
        Init a group of resource resource

        Keyword arguments:
        name -- name given to the resource (id)
        fullname -- long name given to the resource
        """
        __LOG__.debug('** GroupOfResources::__init__ {0}'.format({'name':name}))
        self.name = name
        self.vacations = []
        if fullname is not None:
            self.fullname = fullname
        else:
            self.fullname = name

        self.resources = []

        self.tasks = []
        return

    def add_resource(self, resource):
        """
        Add a resource to the group of resources

        Keyword arguments:
        resource -- Resource object
        """
        if resource not in self.resources:
            self.resources.append(resource)
            resource.add_group(self)
        return


    def add_vacations(self, dfrom, dto=None):
        """
        Add vacations to a resource begining at [dfrom] to [dto] (included). If
        [dto] is not defined, vacation will be for [dfrom] day only

        Keyword arguments:
        dfrom -- datetime.date begining of vacation
        dto -- datetime.date end of vacation of vacation
        """
        __LOG__.debug('** Resource::add_vacations {0}'.format({'name':self.name, 'dfrom':dfrom, 'dto':dto}))
        if dto is None:
            self.vacations.append((dfrom, dfrom))
        else:
            self.vacations.append((dfrom, dto))
        return



    def nb_elements(self):
        """
        Returns the number of resources
        """
        __LOG__.debug('** GroupOfResources::nb_elements ({0})'.format({'name':self.name}))
        return len(self.resources)



    def is_available(self, date):
        """
        Returns True if any resource is available at given date, False if not.
        Availibility is taken from the global VACATIONS and resource's ones.

        Keyword arguments:
        date -- datetime.date day to look for
        """
        # Global VACATIONS
        if date in VACATIONS:
            __LOG__.debug('** GroupOfResources::is_available {0} : False (global vacation)'.format({'name':self.name, 'date':date}))
            return False

        # Group vacations
        for h in self.vacations:
            dfrom, dto = h
            if date >= dfrom and date <= dto:
                __LOG__.debug('** GroupOfResources::is_available {0} : False (group vacation)'.format({'name':self.name, 'date':date}))
                return False

        # Test if at least one resource is avalaible
        for r in self.resources:
            if r.is_available(date):
                __LOG__.debug('** GroupOfResources::is_available {0} : True {1}'.format({'name':self.name, 'date':date}, r.name))
                return True

        __LOG__.debug('** GroupOfResources::is_available {0} : False'.format({'name':self.name, 'date':date}))
        return False


    def add_task(self, task):
        """
        Tell the resource that we have assigned a task

        Keyword arguments:
        task -- Task object
        """
        if task not in self.tasks:
            self.tasks.append(task)
        return


    def search_for_task_conflicts(self, all_tasks = False):
        """
        Returns a dictionnary of all days (datetime.date) containing for each
        overcharged day the list of task for this day.

        It examines all resources member and group tasks.

        Keyword arguments:
        all_tasks -- if True return all tasks for all days, not just overcharged days
        """
        # Get for each resource
        affected_days = {}
        for r in self.resources:
            ad = r.search_for_task_conflicts(all_tasks = True)
            for d in ad:
                try:
                    affected_days[d].append(ad[d])
                except KeyError:
                    affected_days[d] = [ ad[d] ]

        # inspect project
        for t in self.tasks:
            cday = t.start_date()
            while cday <= t.end_date():
                if cday.weekday() not in NOT_WORKED_DAYS:
                    try:
                        affected_days[cday].append(t.fullname)
                    except KeyError:
                        affected_days[cday] = [t.fullname]
                  
                cday += datetime.timedelta(days=1)


        # compile everything
        overcharged_days = {}
        ke = list(affected_days.keys())
        ke.sort()
        for d in ke:
            affected_days[d] = _flatten(affected_days[d])
            if all_tasks:
                overcharged_days[d] = affected_days[d]

            elif len(affected_days[d]) > self.nb_elements():
                overcharged_days[d] = affected_days[d]
                __LOG__.warning('** GroupOfResources "{2}" has more than {3} tasks on day {0} / {1}'.format(d, affected_days[d], self.name, self.nb_elements()))
                
        return overcharged_days


############################################################################

class Resource(object):
    """
    Class for handling resources assigned to tasks
    """
    def __init__(self, name, fullname=None):
        """
        Init a resource

        Keyword arguments:
        name -- name given to the resource (id)
        fullname -- long name given to the resource
        """
        __LOG__.debug('** Resource::__init__ {0}'.format({'name':name}))
        self.name = name
        if fullname is not None:
            self.fullname = fullname
        else:
            self.fullname = name

        self.vacations = []
        self.member_of_groups = []

        self.tasks = []
        return

    def add_vacations(self, dfrom, dto=None):
        """
        Add vacations to a resource begining at [dfrom] to [dto] (included). If
        [dto] is not defined, vacation will be for [dfrom] day only

        Keyword arguments:
        dfrom -- datetime.date begining of vacation
        dto -- datetime.date end of vacation of vacation
        """
        __LOG__.debug('** Resource::add_vacations {0}'.format({'name':self.name, 'dfrom':dfrom, 'dto':dto}))
        if dto is None:
            self.vacations.append((dfrom, dfrom))
        else:
            self.vacations.append((dfrom, dto))
        return


    def nb_elements(self):
        """
        Returns the number of resources, 1 here
        """
        __LOG__.debug('** Resource::nb_elements ({0})'.format({'name':self.name}))
        return 1


    def is_available(self, date):
        """
        Returns True if the resource is available at given date, False if not.
        Availibility is taken from the global VACATIONS and resource's ones.

        Keyword arguments:
        date -- datetime.date day to look for
        """
        # global VACATIONS
        if date in VACATIONS:
            __LOG__.debug('** Resource::is_available {0} : False (global vacation)'.format({'name':self.name, 'date':date}))
            return False
        
        # GroupOfResources vacation
        for g in self.member_of_groups:
            for h in g.vacations:
                dfrom, dto = h
                if date >= dfrom and date <= dto:
                    __LOG__.debug('** Resource::is_available {0} : False (Group {1})'.format({'name':self.name, 'date':date}, g.name))
                    return False
        

        # Resource vacation
        for h in self.vacations:
            dfrom, dto = h
            if date >= dfrom and date <= dto:
                __LOG__.debug('** Resource::is_available {0} : False'.format({'name':self.name, 'date':date}))
                return False
        __LOG__.debug('** Resource::is_available {0} : True'.format({'name':self.name, 'date':date}))
        return True


    def add_group(self, groupofresources):
        """
        Tell the resource it belongs to a GroupOfResources
        
        Keyword arguments:
        groupofresources -- GroupOfResources
        """
        if groupofresources not in self.member_of_groups:
            self.member_of_groups.append(groupofresources)
        return


    def add_task(self, task):
        """
        Tell the resource that we have assigned a task

        Keyword arguments:
        task -- Task object
        """
        if task not in self.tasks:
            self.tasks.append(task)
        return


    def search_for_task_conflicts(self, all_tasks=False):
        """
        Returns a dictionnary of all days (datetime.date) containing for each
        overcharged day the list of task for this day.

        Keyword arguments:
        all_tasks -- if True return all tasks for all days, not just overcharged days
        """
        affected_days = {}
        for t in self.tasks:
            cday = t.start_date()
            while cday <= t.end_date():
                if cday.weekday() not in NOT_WORKED_DAYS:
                    try:
                        affected_days[cday].append(t.fullname)
                    except KeyError:
                        affected_days[cday] = [t.fullname]
                    
                cday += datetime.timedelta(days=1)

        # return all
        if all_tasks:
            return affected_days

        # compile only overcharge
        overcharged_days = {}
        ke = list(affected_days.keys())
        ke.sort()
        for d in ke:
            if len(affected_days[d]) > 1:
                overcharged_days[d] = affected_days[d]
                __LOG__.warning('** Resource "{2}" has more than one task on day {0} / {1}'.format(d, affected_days[d], self.name))
                
        return overcharged_days
            


############################################################################


class Task(object):
    """
    Class for manipulating Tasks
    """
    def __init__(self, name, start=None, stop=None, duration=None, depends_of=None, resources=None, percent_done=0, color=None, fullname=None):
        """
        Initialize task object. Two of start, stop or duration may be given.
        This task can rely on other task and will be completed with resources.
        If percent done is given, a progress bar will be included on the task.
        If color is specified, it will be used for the task.

        Keyword arguments:
        name -- name of the task (id)
        fullname -- long name given to the resource
        start -- datetime.date, first day of the task, default None
        stop -- datetime.date, last day of the task, default None
        duration -- int, duration of the task, default None
        depends_of -- list of Task which are parents of this one, default None
        resources -- list of Resources assigned to the task, default None
        percent_done -- int, percent of achievment, default 0
        color -- string, html color, default None
        """
        __LOG__.debug('** Task::__init__ {0}'.format({'name':name, 'start':start, 'stop':stop, 'duration':duration, 'depends_of':depends_of, 'resources':resources, 'percent_done':percent_done}))
        self.name = name
        if fullname is not None:
            self.fullname = fullname
        else:
            self.fullname = name

        self.start = start
        self.stop = stop
        self.duration = duration
        self.color = color

        ends = (self.start, self.stop, self.duration)
        nonecount = 0
        for e in ends:
            if e is None:
                nonecount += 1

        # check limits (2 must be set on 4) or scheduling is defined by duration and dependencies
        if nonecount != 1 and  (self.duration is None or depends_of is None):
            __LOG__.error('** Task "{1}" must be defined by two of three limits ({0})'.format({'start':self.start, 'stop':self.stop, 'duration':self.duration}, fullname))
            # Bug ? may be defined later
            #raise ValueError('Task "{1}" must be defined by two of three limits ({0})'.format({'start':self.start, 'stop':self.stop, 'duration':self.duration}, fullname))

        if type(depends_of) is type([]):
            self.depends_of = depends_of
        elif depends_of is not None:
            self.depends_of = [depends_of]
        else:
            self.depends_of = None

        self.resources = resources
        self.percent_done = percent_done
        self.drawn_x_begin_coord = None
        self.drawn_x_end_coord = None
        self.drawn_y_coord = None
        self.cache_start_date = None
        self.cache_end_date = None

        # tell each resource we have
        # assigned a new task
        if resources is not None:
            for r in resources:
                r.add_task(self)

        return


    def add_depends(self, depends_of):
        """
        Adds dependency to a task

        Keyword arguments:
        depends_of -- list of Task which are parents of this one
        """
        if type(depends_of) is type([]):
            if self.depends_of is None:
                self.depends_of = depends_of
            else:
                for d in depends_of:
                    self.depends_of.append(d)
        else:
            if self.depends_of is None:
                self.depends_of = depends_of
            else:
                self.depends_of.append(depends_of)

        return


    def start_date(self):
        """
        Returns the first day of the task, either the one which was given at
        task creation or the one calculated after checking dependencies
        """
        if self.cache_start_date is not None:
            return self.cache_start_date

        __LOG__.debug('** Task::start_date ({0})'.format(self.name))
        if self.start is not None:
            # start date setted, calculate begining
            if self.depends_of is None:
                # depends of nothing... start date is start
                #__LOG__.debug('*** Do not depend of other task')
                start = self.start
                while start.weekday() in NOT_WORKED_DAYS or start in VACATIONS:
                    start = start + datetime.timedelta(days=1)

                if start > self.start:
                    __LOG__.warning('** Due to vacations, Task "{0}", will not start on date {1} but {2}'.format(self.fullname, self.start, start))

                self.cache_start_date = start
                return self.cache_start_date
            else:
                # depends of other task, start date could vary
                #__LOG__.debug('*** Do depend of other tasks')
                start = self.start
                while start.weekday() in NOT_WORKED_DAYS or start in VACATIONS:
                    start = start + datetime.timedelta(days=1)

                prev_task_end = start
                for t in self.depends_of:
                    if t.end_date() >= prev_task_end:
                        #__LOG__.debug('*** latest one {0} which end on {1}'.format(t.name, t.end_date()))
                        prev_task_end = t.end_date() + datetime.timedelta(days=1)

                while prev_task_end.weekday() in NOT_WORKED_DAYS or prev_task_end in VACATIONS:
                    prev_task_end = prev_task_end + datetime.timedelta(days=1)

                if prev_task_end > self.start:
                    __LOG__.warning('** Due to dependencies, Task "{0}", will not start on date {1} but {2}'.format(self.fullname, self.start, prev_task_end))

                self.cache_start_date = prev_task_end
                return self.cache_start_date

        elif self.duration is None: # start and stop fixed
            current_day = self.start
            # check depends
            if self.depends_of is not None:
                prev_task_end = self.depends_of[0].end_date()
                for t in self.depends_of:
                    if t.end_date() > prev_task_end:
                        #__LOG__.debug('*** latest one {0} which end on {1}'.format(t.name, t.end_date()))
                        prev_task_end = t.end_date()
                if prev_task_end > current_day:
                    depend_start_date = prev_task_end
                else:
                    start = self.start
                    while start.weekday() in NOT_WORKED_DAYS or start in VACATIONS:
                        start = start + datetime.timedelta(days=1)
                    depend_start_date = start

                    if depend_start_date > current_day:
                        __LOG__.error('** Due to dependencies, Task "{0}", could not be finished on time (should start as last on {1} but will start on {2})'.format(self.fullname, current_day, depend_start_date))
                    self.cache_start_date = depend_start_date           
            else:
                # should be first day of start...
                self.cache_start_date = current_day            

            return self.cache_start_date

        elif self.duration is not None and self.depends_of is not None and self.stop is None :  # duration and dependencies fixed
            prev_task_end = self.depends_of[0].end_date()
            for t in self.depends_of:
                if t.end_date() > prev_task_end:
                    __LOG__.debug('*** latest one {0} which end on {1}'.format(t.name, t.end_date()))
                    prev_task_end = t.end_date()

            start = prev_task_end + datetime.timedelta(days=1)
            
            while start.weekday() in NOT_WORKED_DAYS or start in VACATIONS:
                start = start + datetime.timedelta(days=1)

            # should be first day of start...
            self.cache_start_date = start

        elif self.start is None and self.stop is not None: # stop and duration fixed
            # start date not setted, calculate from end_date + depends
            current_day = self.stop
            real_duration = 0
            duration = self.duration 
            while duration > 0:
                if not (current_day.weekday() in NOT_WORKED_DAYS or current_day in VACATIONS):
                    real_duration = real_duration + 1
                    duration -= 1
                else:
                    real_duration = real_duration + 1

                current_day = self.stop - datetime.timedelta(days=real_duration)
            current_day = self.stop - datetime.timedelta(days=real_duration - 1)

            # check depends
            if self.depends_of is not None:
                prev_task_end = self.depends_of[0].end_date()
                for t in self.depends_of:
                    if t.end_date() > prev_task_end:
                        __LOG__.debug('*** latest one {0} which end on {1}'.format(t.name, t.end_date()))
                        prev_task_end = t.end_date()

                if prev_task_end > current_day:
                    start = prev_task_end + datetime.timedelta(days=1)
                    #return prev_task_end
                else:
                    start = current_day

                
                while start.weekday() in NOT_WORKED_DAYS or start in VACATIONS:
                    start = start + datetime.timedelta(days=1)

                depend_start_date = start

                if depend_start_date > current_day:
                    __LOG__.error('** Due to dependencies, Task "{0}", could not be finished on time (should start as last on {1} but will start on {2})'.format(self.fullname, current_day, depend_start_date))
                    self.cache_start_date = depend_start_date           
                else:
                    # should be first day of start...
                    self.cache_start_date = depend_start_date
            else:
                # should be first day of start...
                self.cache_start_date = current_day            


        if self.cache_start_date != self.start:
            __LOG__.warning('** starting date for task "{0}" is changed from {1} to {2}'.format(self.fullname, self.start, self.cache_start_date))
        return self.cache_start_date


    def end_date(self):
        """
        Returns the last day of the task, either the one which was given at task
        creation or the one calculated after checking dependencies
        """
        # Should take care of resources vacations ?
        if self.cache_end_date is not None:
            return self.cache_end_date

        __LOG__.debug('** Task::end_date ({0})'.format(self.name))

        if self.duration is None or self.start is None and self.stop is not None:
            real_end = self.stop
            # Take care of vacations
            while real_end.weekday() in NOT_WORKED_DAYS or real_end in VACATIONS:
                real_end -= datetime.timedelta(days=1)

            if real_end <= self.start_date():
                current_day = self.start_date()
                real_duration = 0
                duration = self.duration   
                while duration > 1 or (current_day.weekday() in NOT_WORKED_DAYS or current_day in VACATIONS):
                    if not (current_day.weekday() in NOT_WORKED_DAYS or current_day in VACATIONS):
                        real_duration = real_duration + 1
                        duration -= 1
                    else:
                        real_duration = real_duration + 1
        
                    current_day = self.start_date() + datetime.timedelta(days=real_duration)
        
                self.cache_end_date = self.start_date() + datetime.timedelta(days=real_duration)
                __LOG__.warning('** task "{0}" will not be finished on time : end_date is changed from {1} to {2}'.format(self.fullname, self.stop, self.cache_end_date))
                return self.cache_end_date
                    

            self.cache_end_date = real_end
            if real_end != self.stop:
                __LOG__.warning('** task "{0}" will not be finished on time : end_date is changed from {1} to {2}'.format(self.fullname, self.stop, self.cache_end_date))


                
            return self.cache_end_date

        if self.stop is None:
            current_day = self.start_date()
            real_duration = 0
            duration = self.duration   
            while duration > 1 or (current_day.weekday() in NOT_WORKED_DAYS or current_day in VACATIONS):
                if not (current_day.weekday() in NOT_WORKED_DAYS or current_day in VACATIONS):
                    real_duration = real_duration + 1
                    duration -= 1
                else:
                    real_duration = real_duration + 1
    
                current_day = self.start_date() + datetime.timedelta(days=real_duration)
    
            self.cache_end_date = self.start_date() + datetime.timedelta(days=real_duration)
            return self.cache_end_date

        raise(ValueError)
        return None

    def svg(self, prev_y=0, start=None, end=None, color=None, level=None):
        """
        Return SVG for drawing this task.

        Keyword arguments:
        prev_y -- int, line to start to draw
        start -- datetime.date of first day to draw
        end -- datetime.date of last day to draw
        color -- string of color for drawing the project
        level -- int, indentation level of the project, not used here
        """
        __LOG__.debug('** Task::svg ({0})'.format({'name':self.name, 'prev_y':prev_y, 'start':start, 'end':end, 'color':color, 'level':level}))

        add_modified_begin_mark = False
        add_modified_end_mark = False

        if start is None:
            start = self.start_date()

        if self.start_date() != self.start and self.start is not None:
            add_modified_begin_mark = True

        if end is None:
            end = self.end_date()

        if self.end_date() != self.stop and self.stop is not None:
            add_modified_end_mark = True

        # override project color if defined
        if self.color is not None:
            color = self.color

        add_begin_mark = False
        add_end_mark = False

        y = prev_y * 10
                    
        # cas 1 -s--S==E--e-
        if self.start_date() >= start and self.end_date() <= end:
            x = (self.start_date() - start).days * 10
            d = ((self.end_date() - self.start_date()).days + 1) * 10
            self.drawn_x_begin_coord = x
            self.drawn_x_end_coord = x+d
       # cas 5 -s--e--S==E-
        elif self.start_date() >= end:
            return (None, 0)
        # cas 6 -S==E-s--e-
        elif self.end_date() <= start:
            return (None, 0)
        # cas 2 -S==s==E--e-
        elif self.start_date() < start and self.end_date() <= end:
            x = 0
            d = ((self.end_date() - start).days) * 10
            self.drawn_x_begin_coord = x
            self.drawn_x_end_coord = x+d
            add_begin_mark = True
        # cas 3 -s--S==e==E-
        elif self.start_date() >= start and  self.end_date() > end:
            x = (self.start_date() - start).days * 10
            d = ((end - self.start_date()).days) * 10
            self.drawn_x_begin_coord = x
            self.drawn_x_end_coord = x+d
            add_end_mark = True
        # cas 4 -S==s==e==E-
        elif self.start_date() < start and self.end_date() > end:
            x = 0
            d = ((end - start).days) * 10
            self.drawn_x_begin_coord = x
            self.drawn_x_end_coord = x+d
            add_end_mark = True
            add_begin_mark = True
        else:
            return (None, 0)

        self.drawn_y_coord = y
        

        svg = svgwrite.container.Group(id=self.name.replace(' ', '_'))
        svg.add(svgwrite.shapes.Rect(
                insert=((x+1)*mm, (y+1)*mm),
                size=((d-2)*mm, 8*mm),
                fill=color,
                stroke=color,
                stroke_width=2,
                opacity=0.85,
                ))
        svg.add(svgwrite.shapes.Rect(
                insert=((x+1)*mm, (y+6)*mm),
                size=(((d-2))*mm, 3*mm),
                fill="#909090",
                stroke=color,
                stroke_width=1,
                opacity=0.2,
                ))

        if add_modified_begin_mark:
            svg.add(svgwrite.shapes.Rect(
                    insert=((x+1)*mm, (y+1)*mm),
                    size=(5*mm, 4*mm),
                    fill="#0000FF",
                    stroke=color,
                    stroke_width=1,
                    opacity=0.35,
                    ))

        if add_modified_end_mark:
            svg.add(svgwrite.shapes.Rect(
                    insert=((x+d-7+1)*mm, (y+1)*mm),
                    size=(5*mm, 4*mm),
                    fill="#0000FF",
                    stroke=color,
                    stroke_width=1,
                    opacity=0.35,
                    ))
        

        if add_begin_mark:
            svg.add(svgwrite.shapes.Rect(
                    insert=((x+1)*mm, (y+1)*mm),
                    size=(5*mm, 8*mm),
                    fill="#000000",
                    stroke=color,
                    stroke_width=1,
                    opacity=0.2,
                    ))
        if add_end_mark:
            svg.add(svgwrite.shapes.Rect(
                    insert=((x+d-7+1)*mm, (y+1)*mm),
                    size=(5*mm, 8*mm),
                    fill="#000000",
                    stroke=color,
                    stroke_width=1,
                    opacity=0.2,
                    ))

        if self.percent_done is not None and self.percent_done > 0:
            # Bar shade
            svg.add(svgwrite.shapes.Rect(
                    insert=((x+1)*mm, (y+6)*mm),
                    size=(((d-2)*self.percent_done/100)*mm, 3*mm),
                    fill="#F08000",
                    stroke=color,
                    stroke_width=1,
                    opacity=0.35,
                ))

        svg.add(svgwrite.text.Text(self.fullname, insert=((x+2)*mm, (y + 5)*mm), fill='black', stroke='black', stroke_width=0, font_family="Verdana", font_size="15"))

        if self.resources is not None:
            t = " / ".join(["{0}".format(r.name) for r in self.resources])
            svg.add(svgwrite.text.Text("{0}".format(t), insert=((x+2)*mm, (y + 8.5)*mm), fill='purple', stroke='black', stroke_width=0, font_family="Verdana", font_size="10"))


        return (svg, 1)


    def svg_dependencies(self, prj):
        """
        Draws svg dependencies between task and project according to coordinates
        cached when drawing tasks

        Keyword arguments:
        prj -- Project object to check against
        """
        __LOG__.debug('** Task::svg_dependencies ({0})'.format({'name':self.name, 'prj':prj}))
        if self.depends_of is None:
            return None
        else:
            svg = svgwrite.container.Group()
            for t in self.depends_of:
                if not (t.drawn_x_end_coord is None or t.drawn_y_coord is None or self.drawn_x_begin_coord is None) and prj.is_in_project(t):
                    svg.add(svgwrite.shapes.Line(
                            start=((t.drawn_x_end_coord-2)*mm, (t.drawn_y_coord+5)*mm), 
                            end=((self.drawn_x_begin_coord)*mm, (t.drawn_y_coord+5)*mm), 
                            stroke='black',
                            stroke_dasharray='5,3',
                            ))

                    marker = svgwrite.container.Marker(insert=(5,5), size=(10,10))
                    marker.add(svgwrite.shapes.Circle((5, 5), r=5, fill='#000000', opacity=0.5, stroke_width=0))
                    svg.add(marker)
                    eline = svgwrite.shapes.Line(
                        start=((self.drawn_x_begin_coord)*mm, (t.drawn_y_coord+5)*mm), 
                        end=((self.drawn_x_begin_coord)*mm, (self.drawn_y_coord + 5)*mm), 
                        stroke='black',
                        stroke_dasharray='5,3',
                        )
                    eline['marker-end'] = marker.get_funciri()
                    svg.add(eline)

        return svg


    def nb_elements(self):
        """
        Returns the number of task, 1 here
        """
        __LOG__.debug('** Task::nb_elements ({0})'.format({'name':self.name}))
        return 1


    def _reset_coord(self):
        """
        Reset cached elements of task
        """
        __LOG__.debug('** Task::reset_coord ({0})'.format({'name':self.name}))
        self.drawn_x_begin_coord = None
        self.drawn_x_end_coord = None
        self.drawn_y_coord = None
        self.cache_start_date = None
        self.cache_end_date = None
        return


    def is_in_project(self, task):
        """
        Return True if the given Task is itself... (lazy coding ;)
        
        Keyword arguments:
        task -- Task object 
        """
        __LOG__.debug('** Task::is_in_project ({0})'.format({'name':self.name, 'task':task}))
        if task is self:
            return True

        return False


    def get_resources(self):
        """
        Returns Resources used in the task
        """
        return self.resources



    def check_conflicts_between_task_and_resources_vacations(self):
        """
        Displays a warning for each conflict between tasks and vacation of
        resources affected to the task

        And returns a dictionnary for resource vacation conflicts
        """
        conflicts = []
        if self.get_resources() is None:
            return conflicts
        for r in self.get_resources():
            cday = self.start_date()
            while cday <= self.end_date():
                if cday.weekday() not in NOT_WORKED_DAYS and not r.is_available(cday):
                    conflicts.append({'resource':r.name,'date':cday, 'task':self.name})
                    __LOG__.warning('** Caution resource "{0}" is affected on task "{2}" during vacations on day {1}'.format(r.name, cday, self.fullname))
                cday += datetime.timedelta(days=1)
        return conflicts


############################################################################


class Project(object):
    """
    Class for handling projects
    """
    def __init__(self, name="", color=None):
        """
        Initialize project with a given name and color for all tasks

        Keyword arguments:
        name -- string, name of the project
        color -- color for all tasks of the project
        """
        self.tasks = []
        self.name = name
        if color is None:
            self.color = '#FFFF90'
        else:
            self.color = color

        self.cache_nb_elements = None
        return

    def add_task(self, task):
        """
        Add a Task to the Project. Task can also be a subproject

        Keyword arguments:
        task -- Task or Project object
        """
        self.tasks.append(task)
        self.cache_nb_elements = None
        return

    def _svg_calendar(self, maxx, maxy, start_date, today=None):
        """
        Draw calendar in svg, begining at start_date for maxx days, containing
        maxy lines. If today is given, draw a blue line at date

        Keyword arguments:
        maxx -- number of days to draw
        maxy -- number of lines to draw
        start_date -- datetime.date of the first day to draw
        today -- datetime.date of day as today reference
        """
        dwg = svgwrite.container.Group()

        cal = {0:'Mo', 1:'Tu', 2:'We', 3:'Th', 4:'Fr', 5:'Sa', 6:'Su'}
    
        maxx += 1

        vlines = dwg.add(svgwrite.container.Group(id='vlines', stroke='lightgray'))
        for x in range(maxx):
            vlines.add(svgwrite.shapes.Line(start=(x*cm, 1*cm), end=(x*cm, (maxy+1)*cm)))
            if (start_date + datetime.timedelta(days=x)).weekday() in NOT_WORKED_DAYS or (start_date + datetime.timedelta(days=x)) in VACATIONS:
                vlines.add(svgwrite.shapes.Rect(
                    insert=(x*cm, 1*cm),
                    size=(1*cm, maxy*cm),
                    fill='gray',
                    stroke='lightgray',
                    stroke_width=1,
                    opacity=0.7,
                    ))
            jour = start_date + datetime.timedelta(days=x)
            if not today is None and today == jour:
                vlines.add(svgwrite.shapes.Rect(
                    insert=((x+0.4)*cm, 0.5*cm),
                    size=(0.2*cm, (0.5+maxy)*cm),
                    fill='lightblue',
                    stroke='lightgray',
                    stroke_width=0,
                    opacity=0.8
                    ))
            vlines.add(svgwrite.text.Text('{2}.{0:02}/{1:02}'.format(jour.day, jour.month, cal[jour.weekday()][0]), insert=((x*10+1)*mm, 9*mm), fill='black', stroke='black', stroke_width=0, font_family="Verdana", font_size="8"))

            daytext = []

            if jour.day == 1 and jour.month == 1:
                vlines.add(svgwrite.text.Text('{0}'.format(jour.year), insert=((x*10+1)*mm, 3*mm), fill='#800000', stroke='#800000', stroke_width=0, font_family="Verdana", font_size="12"))
            
            if jour.weekday() == 0:
                daytext.append('W:{0:02}'.format(jour.isocalendar()[1]))

            if jour.day == 1:
                daytext.append('{0}'.format(jour.strftime("%B")[:3]))

            if len(daytext) > 0:
                vlines.add(svgwrite.text.Text(' / '.join(daytext), insert=((x*10+1)*mm, 6*mm), fill='black', stroke='black', stroke_width=0, font_family="Verdana", font_size="12"))

        vlines.add(svgwrite.shapes.Line(start=(maxx*cm, 1*cm), end=(maxx*cm, (maxy+1)*cm)))


        hlines = dwg.add(svgwrite.container.Group(id='hlines', stroke='lightgray'))
        for y in range(1, maxy+2):
            hlines.add(svgwrite.shapes.Line(start=(0*cm, y*cm), end=(maxx*cm, y*cm)))

        return dwg


    def make_svg_for_tasks(self, filename, today=None, start=None, end=None):
        """
        Draw gantt of tasks and output it to filename. If start or end are
        given, use them as reference, otherwise use project first and last day

        Keyword arguments:
        filename -- string, filename to save to
        today -- datetime.date of day marked as a reference
        start -- datetime.date of first day to draw
        end -- datetime.date of last day to draw
        """
        if len(self.tasks) == 0:
            __LOG__.warning('** Empty project : {0}'.format(self.name))
            return


        self._reset_coord()

        if start is None:
            start_date = self.start_date()    
        else:
            start_date = start

        if end is None:
            end_date = self.end_date() 
        else:
            end_date = end


        if start_date > end_date:
            __LOG__.critical('start date {0} > end_date {1}'.format(start_date, end_date))
            sys.exit(1)

        maxx = (end_date - start_date).days 

        ldwg = svgwrite.container.Group()
    
        psvg, pheight = self.svg(prev_y=1, start=start_date, end=end_date, color = self.color)
        ldwg.add(psvg)
        dep = self.svg_dependencies(self)
        if dep is not None:
            ldwg.add(dep)

        dwg = svgwrite.Drawing(filename, debug=True)
        dwg.add(svgwrite.shapes.Rect(
                    insert=(0*cm, 0*cm),
                    size=((maxx+1)*cm, (pheight+1)*cm),
                    fill='white',
                    stroke_width=0,
                    opacity=1
                    ))

        dwg.add(self._svg_calendar(maxx, pheight, start_date, today))
        dwg.add(ldwg)
        dwg.save()
        return

    def make_svg_for_resources(self, filename, today=None, start=None, end=None, resources=None, one_line_for_tasks=False):
        """
        Draw resources affectation and output it to filename. If start or end are
        given, use them as reference, otherwise use project first and last day

        And returns to a dictionnary of dictionnaries for vacation and task
        conflicts for resources

        Keyword arguments:
        filename -- string, filename to save to
        today -- datetime.date of day marked as a reference
        start -- datetime.date of first day to draw
        end -- datetime.date of last day to draw
        resources -- list of Resource to check, default all
        one_line_for_tasks -- use only one line to display all tasks ?
        """

        if len(self.tasks) == 0:
            __LOG__.warning('** Empty project : {0}'.format(self.name))
            return

        self._reset_coord()


        if start is None:
            start_date = self.start_date()    
        else:
            start_date = start

        if end is None:
            end_date = self.end_date() 
        else:
            end_date = end


        if start_date > end_date:
            __LOG__.critical('start date {0} > end_date {1}'.format(start_date, end_date))
            sys.exit(1)


        if resources is None:
            resources = self.get_resources()

        maxx = (end_date - start_date).days 
        maxy = len(resources) * 2

        if maxy == 0:
            # No resources
            return {}


        # detect conflicts between resources and holidays
        conflicts_vacations = []
        for t in self.get_tasks():
            conflicts_vacations.append(t.check_conflicts_between_task_and_resources_vacations())

        conflicts_vacations = _flatten(conflicts_vacations)


        ldwg = svgwrite.container.Group()
    
        nline = 1
        conflicts_tasks = []
        conflict_display_line = 1
        for r in resources:
            # do stuff for each resource
            ress = svgwrite.container.Group()
            ress.add(svgwrite.text.Text('{0}'.format(r.fullname), insert=(3*mm, (nline*10+7)*mm), fill='black', stroke='white', stroke_width=0, font_family="Verdana", font_size="18"))
            ldwg.add(ress)


            overcharged_days = r.search_for_task_conflicts()


            conflict_display_line = nline
            nline += 1

            vac = svgwrite.container.Group()
            conflicts = svgwrite.container.Group()
            cday = start_date
            while cday <= end_date:
                # Vacations
                if cday.weekday() not in NOT_WORKED_DAYS and cday not in VACATIONS and not r.is_available(cday):
                     vac.add(svgwrite.shapes.Rect(
                            insert=(((cday - start_date).days * 10 + 1)*mm, ((conflict_display_line)*10+1)*mm),
                            size=(4*mm, 8*mm),
                            fill="#00AA00",
                            stroke="#00AA00",
                            stroke_width=1,
                            opacity=0.65,
                            ))

                # Overcharge
                if cday.weekday() not in NOT_WORKED_DAYS and cday not in VACATIONS and cday in overcharged_days:
                    conflicts.add(svgwrite.shapes.Rect(
                        insert=(((cday - start_date).days * 10 + 1 + 4)*mm, ((conflict_display_line)*10+1)*mm),
                        size=(4*mm, 8*mm),
                        fill="#AA0000",
                        stroke="#AA0000",
                        stroke_width=1,
                        opacity=0.65,
                        ))
                
                cday += datetime.timedelta(days=1)

            ldwg.add(vac)
            ldwg.add(conflicts)

            for t in self.get_tasks():
                if t.get_resources() is not None and r in t.get_resources():
                    psvg, void = t.svg(prev_y = nline, start=start_date, end=end_date, color=self.color)
                    if psvg is not None:
                        ldwg.add(psvg)
                        if not one_line_for_tasks:
                            nline += 1


            if not one_line_for_tasks:
                ldwg.add(
                    svgwrite.shapes.Line(
                        start=((0)*cm, (nline)*cm), 
                        end=((maxx+1)*cm, (nline)*cm), 
                        stroke='black',
                        ))
                
            # nline += 1
            if one_line_for_tasks:
                nline += 1


        dwg = svgwrite.Drawing(filename, debug=True)
        dwg.add(svgwrite.shapes.Rect(
                    insert=(0*cm, 0*cm),
                    size=((maxx+1)*cm, (nline)*cm),
                    fill='white',
                    stroke_width=0,
                    opacity=1
                    ))
        dwg.add(self._svg_calendar(maxx, nline-1, start_date, today))
        dwg.add(ldwg)
        dwg.save()
        return {
            'conflicts_vacations': conflicts_vacations, 
            'conflicts_tasks':conflicts_tasks
            }


    def start_date(self):
        """
        Returns first day of the project
        """
        if len(self.tasks) == 0:
            __LOG__.warning('** Empty project : {0}'.format(self.name))
            return datetime.date(9999, 1, 1)
        
        first = self.tasks[0].start_date()
        for t in self.tasks:
            if t.start_date() < first:
                first = t.start_date()
        return first


    def end_date(self):
        """
        Returns last day of the project
        """
        if len(self.tasks) == 0:
            __LOG__.warning('** Empty project : {0}'.format(self.name))
            return datetime.date(1970, 1, 1)

        last = self.tasks[0].end_date()
        for t in self.tasks:
            if t.end_date() > last:
                last = t.end_date()
        return last

    def svg(self, prev_y=0, start=None, end=None, color=None, level=0):
        """
        Return (SVG code, number of lines drawn) for the project. Draws all
        tasks and add project name with a purple bar on the left side.

        Keyword arguments:
        prev_y -- int, line to start to draw
        start -- datetime.date of first day to draw
        end -- datetime.date of last day to draw
        color -- string of color for drawing the project
        level -- int, indentation level of the project
        """
        if start is None:
            start = self.start_date()
        if end is None:
            end = self.end_date()
        if color is None or self.color is not None:
            color = self.color


        cy = prev_y + 1*(self.name != "")

        prj = svgwrite.container.Group()

        for t in self.tasks:
            trepr, theight = t.svg(cy, start=start, end=end, color=color, level=level+1)
            if trepr is not None:
                prj.add(trepr)
                cy += theight

        fprj = svgwrite.container.Group()
        if self.name != "":
            # if ((self.start_date() >= start and self.end_date() <= end) 
            #     or (self.start_date() >= start and (self.end_date() <= end or self.start_date() <= end))) or level == 1: 
            if ((self.start_date() >= start and self.end_date() <= end) 
                or ((self.end_date() >=start and self.start_date() <= end))) or level == 1: 
                fprj.add(svgwrite.text.Text('{0}'.format(self.name), insert=((6*level+3)*mm, ((prev_y)*10+7)*mm), fill='black', stroke='white', stroke_width=0, font_family="Verdana", font_size="18"))

                fprj.add(svgwrite.shapes.Rect(
                        insert=((6*level+0.8)*mm, (prev_y+0.5)*cm),
                        size=(0.2*cm, ((cy-prev_y-1)+0.4)*cm),
                        fill='purple',
                        stroke='lightgray',
                        stroke_width=0,
                        opacity=0.5
                        ))
            else:
                cy -= 1

        fprj.add(prj)

        return (fprj, cy-prev_y)


    def svg_dependencies(self, prj):
        """
        Draws svg dependencies between tasks according to coordinates cached
        when drawing tasks

        Keyword arguments:
        prj -- Project object to check against
        """
        svg = svgwrite.container.Group()
        for t in self.tasks:
            trepr = t.svg_dependencies(prj)
            if trepr is not None:
                svg.add(trepr)
        return svg


    def nb_elements(self):
        """
        Returns the number of tasks included in the project or subproject
        """
        if self.cache_nb_elements is not None:
            return self.cache_nb_elements
        
        nb = 0
        for t in self.tasks:
            nb += t.nb_elements()

        self.cache_nb_elements = nb
        return nb 

    def _reset_coord(self):
        """
        Reset cached elements of all tasks and project
        """
        self.cache_nb_elements = None
        for t in self.tasks:
            t._reset_coord()
        return

    def is_in_project(self, task):
        """
        Return True if the given Task is in the project, False if not
        
        Keyword arguments:
        task -- Task object 
        """
        for t in self.tasks:
            if t.is_in_project(task):
                return True
        return False


    def get_resources(self):
        """
        Returns Resources used in the project
        """
        rlist = []
        for t in self.tasks:
            r = t.get_resources()
            if r is not None:
                rlist.append(r)

        flist = []
        for r in _flatten(rlist):
            if r not in flist:
                flist.append(r)
        return flist



    def get_tasks(self):
        """
        Returns flat list of Tasks used in the Project and subproject
        """
        tlist = []
        for t in self.tasks:
            # if it is a sub project, recurse
            if type(t) is type(self):
                st = t.get_tasks()
                tlist.append(st)
            else: # get task
                tlist.append(t)

        flist = []
        for r in _flatten(tlist):
            if r not in flist:
                flist.append(r)
        return flist


# MAIN -------------------
if __name__ == '__main__':
    import doctest
    # non regression test
    doctest.testmod()
else:
    #init_log_to_sysout(level=logging.DEBUG)
    init_log_to_sysout(level=logging.WARNING)


#<EOF>######################################################################


