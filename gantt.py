
#!/usr/bin/env python3
# -*- coding: utf-8-unix -*-

"""
gantt.py - version and date, see below

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

Test strings :
^^^^^^^^^^^^

>>> import gantt
>>> gantt.add_vacations(datetime.date(2015, 1, 1))
>>> gantt.add_vacations(datetime.date(2014, 12, 25))

>>> rANO = gantt.Ressource('ANO')
>>> rJLS = gantt.Ressource('JLS')
>>> rANO.add_vacations(
...     dfrom=datetime.date(2015, 1, 2), 
...     dto=datetime.date(2015, 1, 4) 
...     )
>>> rANO.add_vacations(
...     dfrom=datetime.date(2015, 1, 6), 
...     dto=datetime.date(2015, 1, 8) 
...     )
>>> print(rANO.is_available(datetime.date(2015, 1, 5)))
True
>>> print(rANO.is_available(datetime.date(2015, 1, 8)))
False
>>> print(rANO.is_available(datetime.date(2015, 1, 6)))
False
>>> print(rANO.is_available(datetime.date(2015, 1, 2)))
False
>>> print(rANO.is_available(datetime.date(2015, 1, 1)))
False


>>> tSADU = gantt.Task(name='tache SADU', start=datetime.date(2014, 12, 25), duration=4)
>>> (tSADU.start_date(), tSADU.end_date())
(datetime.date(2014, 12, 26), datetime.date(2014, 12, 31))

>>> tSAST = gantt.Task(name='tache SAST', start=datetime.date(2014, 12, 25), stop=datetime.date(2014, 12, 31))
>>> (tSAST.start_date(), tSAST.end_date())
(datetime.date(2014, 12, 26), datetime.date(2014, 12, 31))

>>> tDUST = gantt.Task(name='tache DUST', stop=datetime.date(2014, 12, 31), duration=4)
>>> (tDUST.start_date(), tDUST.end_date())
(datetime.date(2014, 12, 26), datetime.date(2014, 12, 31))

>>> tDUSTSADU = gantt.Task(name='tache DUST SADU', start=datetime.date(2015, 1, 1), duration=4, depends_of=[tDUST])
>>> (tDUSTSADU.start_date(), tDUSTSADU.end_date())
(datetime.date(2015, 1, 2), datetime.date(2015, 1, 7))

>>> tDUSTSAST = gantt.Task(name='tache DUST SAST', start=datetime.date(2015, 1, 1), stop=datetime.date(2015, 1, 7), depends_of=[tDUST])
>>> (tDUSTSAST.start_date(), tDUSTSAST.end_date())
(datetime.date(2015, 1, 2), datetime.date(2015, 1, 7))

>>> tDUSTDUST = gantt.Task(name='tache DUST DUST', stop=datetime.date(2015, 1, 7), duration=9, depends_of=[tDUST])
>>> (tDUSTDUST.start_date(), tDUSTDUST.end_date())
(datetime.date(2015, 1, 2), datetime.date(2015, 1, 7))

>>> tDUSTDUST2 = gantt.Task(name='tache DUST DUST2', stop=datetime.date(2015, 1, 10), duration=2, depends_of=[tDUST])
>>> (tDUSTDUST2.start_date(), tDUSTDUST2.end_date())
(datetime.date(2015, 1, 8), datetime.date(2015, 1, 9))


>>> tSADUSADU = gantt.Task(name='tache SADU SADU', start=datetime.date(2015, 1, 1), duration=4, depends_of=[tSADU])
>>> (tSADUSADU.start_date(), tSADUSADU.end_date())
(datetime.date(2015, 1, 2), datetime.date(2015, 1, 7))

>>> tSADUSAST = gantt.Task(name='tache SADU SAST', start=datetime.date(2015, 1, 1), stop=datetime.date(2015, 1, 7), depends_of=[tSADU])
>>> (tSADUSAST.start_date(), tSADUSAST.end_date())
(datetime.date(2015, 1, 2), datetime.date(2015, 1, 7))

>>> tSADUDUST = gantt.Task(name='tache SADU DUST', stop=datetime.date(2015, 1, 7), duration=9, depends_of=[tSADU])
>>> (tSADUDUST.start_date(), tSADUDUST.end_date())
(datetime.date(2015, 1, 2), datetime.date(2015, 1, 7))

>>> tSADUDUST2 = gantt.Task(name='tache SADU DUST2', stop=datetime.date(2015, 1, 10), duration=2, depends_of=[tSADU])
>>> (tSADUDUST2.start_date(), tSADUDUST2.end_date())
(datetime.date(2015, 1, 8), datetime.date(2015, 1, 9))



>>> tSASTSADU = gantt.Task(name='tache SAST SADU', start=datetime.date(2015, 1, 1), duration=4, depends_of=[tSAST])
>>> (tSASTSADU.start_date(), tSASTSADU.end_date())
(datetime.date(2015, 1, 2), datetime.date(2015, 1, 7))

>>> tSASTSAST = gantt.Task(name='tache SAST SAST', start=datetime.date(2015, 1, 1), stop=datetime.date(2015, 1, 7), depends_of=[tSAST])
>>> (tSASTSAST.start_date(), tSASTSAST.end_date())
(datetime.date(2015, 1, 2), datetime.date(2015, 1, 7))

>>> tSASTDUST = gantt.Task(name='tache SAST DUST', stop=datetime.date(2015, 1, 7), duration=9, depends_of=[tSAST])
>>> (tSASTDUST.start_date(), tSASTDUST.end_date())
(datetime.date(2015, 1, 2), datetime.date(2015, 1, 7))

>>> tSASTDUST2 = gantt.Task(name='tache SAST DUST2', stop=datetime.date(2015, 1, 10), duration=2, depends_of=[tSAST])
>>> (tSASTDUST2.start_date(), tSASTDUST2.end_date())
(datetime.date(2015, 1, 8), datetime.date(2015, 1, 9))


>>> tBUG = gantt.Task(name='tBUG', start=datetime.date(2015, 1, 9), duration=7)
>>> (tBUG.start_date(), tBUG.end_date())
(datetime.date(2015, 1, 9), datetime.date(2015, 1, 19))

>>> tBUG2 = gantt.Task(name='tBUG2', start=datetime.date(2015, 1, 10), duration=7)
>>> (tBUG2.start_date(), tBUG2.end_date())
(datetime.date(2015, 1, 12), datetime.date(2015, 1, 20))

 
>>> p1 = gantt.Project(name='Projet 1')

>>> p1.add_task(tSADU)
>>> p1.add_task(tSAST)
>>> p1.add_task(tDUST)
>>> p1.add_task(tDUSTSADU)
>>> p1.add_task(tDUSTSAST)
>>> p1.add_task(tDUSTDUST)
>>> p1.add_task(tDUSTDUST2)

>>> p1.add_task(tSADUSADU)
>>> p1.add_task(tSADUSAST)
>>> p1.add_task(tSADUDUST)
>>> p1.add_task(tSADUDUST2)

>>> p1.add_task(tSASTSADU)
>>> p1.add_task(tSASTSAST)
>>> p1.add_task(tSASTDUST)
>>> p1.add_task(tSASTDUST2)

>>> p1.add_task(tBUG)
>>> p1.add_task(tBUG2)

>>> p1.make_svg_for_tasks(filename='/tmp/h.svg', today=datetime.date(2014, 12, 31))

"""



__author__ = 'Alexandre Norman (norman at xael.org)'
__version__ = '0.2.0'
__last_modification__ = '2014.12.30'

import datetime
import logging

# https://bitbucket.org/mozman/svgwrite
# http://svgwrite.readthedocs.org/en/latest/
try:
    import svgwrite
except ImportError:
    # if svgwrite is not 'installed' append parent dir of __file__ to sys.path
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.split(os.path.abspath(__file__))[0]+'/..'))

try:
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
    """
    global VACATIONS
    if end_date is None:
        VACATIONS.append(start_date)
    else:
        while start_date <= end_date:               
            VACATIONS.append(start_date)
            start_date += datetime.timedelta(days=1)

    return

############################################################################

def _init_log_to_sysout(level=logging.INFO):
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

class Ressource(object):
    """
    Class for handling ressources assigned to tasks
    """
    def __init__(self, name):
        """
        Init a ressource

        Keyword arguments:
        name -- name given to the ressource
        """
        __LOG__.debug('** Ressource::__init__ {0}'.format({'name':name}))
        self.name = name
        self.vacations = []
        return

    def add_vacations(self, dfrom, dto=None):
        """
        Add vacations to a ressource begining at [dfrom] to [dto] (included). If
        [dto] is not defined, vacation will be for [dfrom] day only

        Keyword arguments:
        dfrom -- datetime.date begining of vacation
        dto -- datetime.date end of vacation of vacation
        """
        __LOG__.debug('** Ressource::add_vacations {0}'.format({'name':self.name, 'dfrom':dfrom, 'dto':dto}))
        if dto is None:
            self.vacations.append((dfrom, dfrom))
        else:
            self.vacations.append((dfrom, dto))
        return

    def is_available(self, date):
        """
        Returns True if the ressource is available at given date, False if not.
        Availibility is taken from the global VACATIONS and ressource's ones.

        Keyword arguments:
        date -- datetime.date day to look for
        """
        if date in VACATIONS:
            __LOG__.debug('** Ressource::is_available {0} : False'.format({'name':self.name, 'date':date}))
            return False
            
        for h in self.vacations:
            dfrom, dto = h
            if date >= dfrom and date <= dto:
                __LOG__.debug('** Ressource::is_available {0} : False'.format({'name':self.name, 'date':date}))
                return False
        __LOG__.debug('** Ressource::is_available {0} : True'.format({'name':self.name, 'date':date}))
        return True


############################################################################


class Task(object):
    """
    Class for manipulating Tasks
    """
    def __init__(self, name, start=None, stop=None, duration=None, depends_of=None, ressources=None, percent_done=0, color=None):
        """
        Initialize task object. Two of start, stop or duration may be given.
        This task can rely on other task and will be completed with ressources.
        If percent done is given, a progress bar will be included on the task.
        If color is specified, it will be used for the task.

        Keyword arguments:
        name -- name of the task
        start -- datetime.date, first day of the task, default None
        stop -- datetime.date, last day of the task, default None
        duration -- int, duration of the task, default None
        depends_of -- list of Task which are parents of thi one, default None
        ressources -- list of Ressources assigned to the task, default None
        percent_done -- int, percent of achievment, default 0
        color -- string, html color, default None
        """
        __LOG__.debug('** Task::__init__ {0}'.format({'name':name, 'start':start, 'stop':stop, 'duration':duration, 'depends_of':depends_of, 'ressources':ressources, 'percent_done':percent_done}))
        self.name = name
        self.start = start
        self.stop = stop
        self.duration = duration
        self.color = color

        ends = (self.start, self.stop, self.duration)
        nonecount = 0
        for e in ends:
            if e is None:
                nonecount += 1

        # check limits (2 must be set on 3)
        if nonecount != 1:
            __LOG__.error('** Task {1} must be defined by two of three limits ({0})'.format({'start':self.start, 'stop':self.stop, 'duration':self.duration}, name))
            raise ValueError('Task {1} must be defined by two of three limits ({0})'.format({'start':self.start, 'stop':self.stop, 'duration':self.duration}, name))

        if type(depends_of) is type([]):
            self.depends_of = depends_of
        elif depends_of is not None:
            self.depends_of = [depends_of]
        else:
            self.depends_of = None

        self.ressources = ressources
        self.percent_done = percent_done
        self.drawn_x_begin_coord = None
        self.drawn_x_end_coord = None
        self.drawn_y_coord = None
        self.cache_start_date = None
        self.cache_end_date = None
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
                        __LOG__.error("** Due to dependencies, Task {0}, could not be finished on time (should start as last on {1} but will start on {2})".format(self.name, current_day, depend_start_date))
                    self.cache_start_date = depend_start_date           
            else:
                # should be first day of start...
                self.cache_start_date = current_day            

            return self.cache_start_date

        elif self.start is None: # stop and duration fixed
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
                    __LOG__.error("** Due to dependencies, Task {0}, could not be finished on time (should start as last on {1} but will start on {2})".format(self.name, current_day, depend_start_date))
                    self.cache_start_date = depend_start_date           
                else:
                    # should be first day of start...
                    self.cache_start_date = depend_start_date
            else:
                # should be first day of start...
                self.cache_start_date = current_day            


        if self.cache_start_date != self.start:
            __LOG__.warning('** starting date for task {0} is changed from {1} to {2}'.format(self.name, self.start, self.cache_start_date))
        return self.cache_start_date


    def end_date(self):
        """
        Returns the last day of the task, either the one which was given at task
        creation or the one calculated after checking dependencies
        """
        # Should take care of ressources vacations ?
        if self.cache_end_date is not None:
            return self.cache_end_date

        __LOG__.debug('** Task::end_date ({0})'.format(self.name))

        if self.duration is None or self.start is None:
            real_end = self.stop
            # Take care of vacations
            while real_end.weekday() in NOT_WORKED_DAYS or real_end in VACATIONS:
                real_end -= datetime.timedelta(days=1)
            self.cache_end_date = real_end
            if real_end != self.stop:
                __LOG__.warning('** ending date for task {0} is changed from {1} to {2}'.format(self.name, self.stop, self.cache_end_date))
                
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

        if self.percent_done > 0:
            # Bar shade
            svg.add(svgwrite.shapes.Rect(
                    insert=((x+1)*mm, (y+6)*mm),
                    size=(((d-2)*self.percent_done/100)*mm, 3*mm),
                    fill="#F08000",
                    stroke=color,
                    stroke_width=1,
                    opacity=0.25,
                ))

        svg.add(svgwrite.text.Text(self.name, insert=((x+2)*mm, (y + 5)*mm), fill='black', stroke='black', stroke_width=0, font_family="Verdana", font_size="15"))

        if self.ressources is not None:
            t = " / ".join(["{0}".format(r.name) for r in self.ressources])
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


    def get_ressources(self):
        """
        Returns Ressources used in the task
        """
        return self.ressources



    def check_conflicts_between_task_and_ressources_vacations(self):
        """
        Displays a warning for each conflict between tasks and vacation of
        ressources affected to the task

        And returns a dictionnary for ressource vacation conflicts
        """
        conflicts = []
        if self.get_ressources() is None:
            return conflicts
        for r in self.get_ressources():
            cday = self.start_date()
            while cday < self.end_date():
                if not r.is_available(cday):
                    conflicts.append({'ressource':r.name,'date':cday, 'task':self.name})
                    __LOG__.warning('** Caution ressource {0} is affected on task {2} during vacations on day {1}'.format(r.name, cday, self.name))
                cday += datetime.timedelta(days=1)
        return conflicts


############################################################################


class Project(object):
    """
    Class for handling projects
    """
    def __init__(self, name="", color='#FFFF90'):
        """
        Initialize project with a given name and color for all tasks

        Keyword arguments:
        name -- string, name of the project
        color -- color for all tasks of the project
        """
        self.tasks = []
        self.name = name
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
            if jour.weekday() == 0:
                daytext.append('W:{0:02}'.format(jour.isocalendar()[1]))

            if jour.day == 1:
                daytext.append('{0}'.format(jour.strftime("%B")[:3]))

            if len(daytext) > 0:
                vlines.add(svgwrite.text.Text(' / '.join(daytext), insert=((x*10+2)*mm, 6*mm), fill='black', stroke='black', stroke_width=0, font_family="Verdana", font_size="12"))

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
        self._reset_coord()

        if start is None:
            start_date = self.start_date()    
        else:
            start_date = start

        if end is None:
            end_date = self.end_date() 
        else:
            end_date = end + datetime.timedelta(days=2)


        maxx = (end_date - start_date).days 
        maxy = self.nb_elements()

        dwg = svgwrite.Drawing(filename, debug=True)
        dwg.add(self._svg_calendar(maxx, maxy, start_date, today))
    
        psvg, pheight = self.svg(prev_y=1, start=start_date, end=end_date, color = self.color)
        dwg.add(psvg)
        dep = self.svg_dependencies(self)
        if dep is not None:
            dwg.add(dep)
        dwg.save()
        return

    def make_svg_for_ressources(self, filename, today=None, start=None, end=None, ressources=None):
        """
        Draw ressources affectation and output it to filename. If start or end are
        given, use them as reference, otherwise use project first and last day

        And returns to a dictionnary of dictionnaries for vacation and task
        conflicts for ressources

        Keyword arguments:
        filename -- string, filename to save to
        today -- datetime.date of day marked as a reference
        start -- datetime.date of first day to draw
        end -- datetime.date of last day to draw
        ressources -- list of Ressource to check, default all
        """
        self._reset_coord()

        if start is None:
            start_date = self.start_date()    
        else:
            start_date = start

        if end is None:
            end_date = self.end_date() 
        else:
            end_date = end + datetime.timedelta(days=1)

        if ressources is None:
            ressources = self.get_ressources()

        maxx = (end_date - start_date).days 
        maxy = len(ressources) * 2

        if maxy == 0:
            # No ressources
            return


        # detect conflicts between ressources and holidays
        conflicts_vacations = []
        for t in self.get_tasks():
            conflicts_vacations.append(t.check_conflicts_between_task_and_ressources_vacations())

        conflicts_vacations = _flatten(conflicts_vacations)


        dwg = svgwrite.Drawing(filename, debug=True)
        dwg.add(self._svg_calendar(maxx, maxy, start_date, today))
    
        nline = 1
        conflicts_tasks = []
        for r in ressources:
            # do stuff for each ressource
            ress = svgwrite.container.Group()
            ress.add(svgwrite.text.Text('{0}'.format(r.name), insert=(3*mm, (nline*10+7)*mm), fill='black', stroke='white', stroke_width=0, font_family="Verdana", font_size="18"))
            dwg.add(ress)

            # and add vacations on the calendar
            vac = svgwrite.container.Group()
            cday = start_date
            while cday < end_date:
                if not r.is_available(cday):
                     vac.add(svgwrite.shapes.Rect(
                            insert=(((cday - start_date).days * 10 + 1)*mm, ((nline)*10+1)*mm),
                            size=(4*mm, 8*mm),
                            fill="#00AA00",
                            stroke="#00AA00",
                            stroke_width=1,
                            opacity=0.65,
                            ))
                cday += datetime.timedelta(days=1)

            dwg.add(vac)

            affected_days = {}
            conflicts = svgwrite.container.Group()
            for t in self.get_tasks():
                if t.get_ressources() is not None and r in t.get_ressources():
                    psvg, void = t.svg(prev_y = nline + 1, start=start_date, end=end_date, color=self.color)
                    dwg.add(psvg)
                    
                    cday = t.start_date()
                    while cday <= t.end_date():
                        if cday in affected_days:
                            conflicts_tasks.append({'ressource':r.name, 'tasks':affected_days[cday], 'day':cday, 'task':t.name })
                            __LOG__.warning('** Conflict between tasks for {0} on date {1} tasks : {2} vs {3}'.format(r.name, cday, ",".join(affected_days[cday]), t.name))

                            vac.add(svgwrite.shapes.Rect(
                                    insert=(((cday - start_date).days * 10 + 1 + 4)*mm, ((nline)*10+1)*mm),
                                    size=(4*mm, 8*mm),
                                    fill="#AA0000",
                                    stroke="#AA0000",
                                    stroke_width=1,
                                    opacity=0.65,
                                    ))

                        try:
                            affected_days[cday].append(t.name)
                        except KeyError:
                            affected_days[cday] = [t.name]

                        cday += datetime.timedelta(days=1)
                    
            dwg.add(conflicts)

            nline += 2

        dwg.save()
        return {
            'conflicts_vacations': conflicts_vacations, 
            'conflicts_tasks':conflicts_tasks
            }


    def start_date(self):
        """
        Returns first day of the project
        """
        first = self.tasks[0].start_date()
        for t in self.tasks:
            if t.start_date() < first:
                first = t.start_date()
        return first


    def end_date(self):
        """
        Returns last day of the project
        """
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

        cy = prev_y
        prj = svgwrite.container.Group()
        if self.name != "":
            prj.add(svgwrite.text.Text('{0}'.format(self.name), insert=((6*level+3)*mm, (cy*10+7)*mm), fill='black', stroke='white', stroke_width=0, font_family="Verdana", font_size="18"))

            prj.add(svgwrite.shapes.Rect(
                    insert=((6*level+0.8)*mm, (cy+0.5)*cm),
                    size=(0.2*cm, (self.nb_elements()-0.6)*cm),
                    fill='purple',
                    stroke='lightgray',
                    stroke_width=0,
                    opacity=0.5
                    ))

            cy += 1
        
        for t in self.tasks:
            trepr, theight = t.svg(cy, start=start, end=end, color=color, level=level+1)
            if trepr is not None:
                prj.add(trepr)
                cy += theight
            
        return (prj, cy-prev_y)


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
        
        nb = 1
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


    def get_ressources(self):
        """
        Returns Ressources used in the project
        """
        rlist = []
        for t in self.tasks:
            r = t.get_ressources()
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
    #_init_log_to_sysout(level=logging.DEBUG)
    _init_log_to_sysout(level=logging.WARNING)


#<EOF>######################################################################


