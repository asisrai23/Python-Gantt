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
>>> r1 = gantt.Ressource('ANO')
>>> r1.add_vacations(
...     dfrom=datetime.date(2015, 1, 2), 
...     dto=datetime.date(2015, 1, 4) 
...     )
>>> r1.add_vacations(
...     dfrom=datetime.date(2015, 1, 6), 
...     dto=datetime.date(2015, 1, 8) 
...     )
>>> print(r1.is_available(datetime.date(2015, 1, 5)))
True
>>> print(r1.is_available(datetime.date(2015, 1, 8)))
False
>>> print(r1.is_available(datetime.date(2015, 1, 6)))
False
>>> print(r1.is_available(datetime.date(2015, 1, 2)))
False
>>> print(r1.is_available(datetime.date(2015, 1, 1)))
False


"""

# Sur les affections de ressources, ajouter un pourcentage ?


__author__ = 'Alexandre Norman (norman at xael.org)'
__version__ = '0.2.0'
__last_modification__ = '2014.12.25'

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

from svgwrite import cm, mm   


############################################################################

__LOG__ = None

############################################################################

# Unworked days (0: Monday... 6: Sunday)
NOT_WORKED_DAYS = [5, 6]

# Vacations as datetime (non worked)
VACATIONS = []

############################################################################

def add_vacations(date):
    """
    """
    global VACATIONS
    VACATIONS.append(date)
    return

############################################################################

def __init_log_to_sysout__(level=logging.INFO):
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

def __show_version__(name, **kwargs):
    """
    Show version
    """
    import os
    print("{0} version {1}".format(os.path.basename(name), __version__))
    return True


############################################################################


def __flatten__(l, ltypes=(list, tuple)):
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

    def add_vacations(self, dfrom, dto):
        """
        Add vacations to a ressource begining at [dfrom] to [dto] (included)

        Keyword arguments:
        dfrom -- datetime.date begining of vacation
        dto -- datetime.date end of vacation of vacation
        """
        __LOG__.debug('** Ressource::add_vacations {0}'.format({'name':self.name, 'dfrom':dfrom, 'dto':dto}))
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
        """
        __LOG__.debug('** Task::__init__ {0}'.format({'name':name, 'start':start, 'stop':stop, 'duration':duration, 'depends_of':depends_of, 'ressources':ressources, 'percent_done':percent_done}))
        self.name = name
        self.start = start
        self.duration = duration
        self.color = color

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
        """
        if self.cache_start_date is not None:
            return self.cache_start_date

        __LOG__.debug('** Task::start_date ({0})'.format(self.name))
        if self.depends_of is None:
            #__LOG__.debug('*** Do not depend of other task')
            start = self.start
            while start.weekday() in NOT_WORKED_DAYS or start in VACATIONS:
                start = start + datetime.timedelta(days=1)
            self.cache_start_date = start
            return start
        else:
            #__LOG__.debug('*** Do depend of other tasks')
            prev_task_end = self.depends_of[0].end_date()
            for t in self.depends_of:
                if t.end_date() > prev_task_end:
                    #__LOG__.debug('*** latest one {0} which end on {1}'.format(t.name, t.end_date()))
                    prev_task_end = t.end_date()
            if prev_task_end > self.start:
                self.cache_start_date = prev_task_end
                return prev_task_end
            else:
                start = self.start
                while start.weekday() in NOT_WORKED_DAYS or start in VACATIONS:
                    start = start + datetime.timedelta(days=1)
                self.cache_start_date = start
                return start


    def end_date(self):
        """
        """
        if self.cache_end_date is not None:
            return self.cache_end_date

        __LOG__.debug('** Task::end_date ({0})'.format(self.name))
        current_day = self.start_date()
        real_duration = 0
        duration = self.duration 
        while duration > 0:
            if not (current_day.weekday() in NOT_WORKED_DAYS or current_day in VACATIONS):
                real_duration = real_duration + 1
                duration -= 1
            else:
                real_duration = real_duration + 1

            current_day = self.start_date() + datetime.timedelta(days=real_duration)

        self.cache_end_date = self.start_date() + datetime.timedelta(days=real_duration)
        return self.cache_end_date


    def svg(self, prev_y=0, start=None, end=None, color=None, level=None):
        """
        """
        __LOG__.debug('** Task::svg ({0})'.format({'name':self.name, 'prev_y':prev_y, 'start':start, 'end':end, 'color':color, 'level':level}))
        if start is None:
            start = self.start_date()
        if end is None:
            end = self.end_date()

        # override project color if defined
        if self.color is not None:
            color = self.color

        add_begin_mark = False
        add_end_mark = False

        y = prev_y * 10
                    
        # cas 1 -s--S==E--e-
        if self.start_date() >= start and self.end_date() <= end:
            x = (self.start_date() - start).days * 10
            d = ((self.end_date() - self.start_date()).days) * 10
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
        """
        __LOG__.debug('** Task::nb_elements ({0})'.format({'name':self.name}))
        return 1


    def reset_coord(self):
        """
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



    def check_conflict_between_task_and_ressources_vacations(self):
        """
        """
        if self.get_ressources() is None:
            return
        for r in self.get_ressources():
            cday = self.start_date()
            while cday < self.end_date():
                if not r.is_available(cday):
                    __LOG__.warning('** Caution ressource {0} is affected on task {2} during vacations on day {1}'.format(r.name, cday, self.name))
                cday += datetime.timedelta(days=1)
        return


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

    def svg_calendar(self, maxx, maxy, start_date, today=None):
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
            vlines.add(svgwrite.text.Text('{2}{0:02}/{1:02}'.format(jour.day, jour.month, cal[jour.weekday()][0]), insert=((x*10+1)*mm, 9*mm), fill='black', stroke='black', stroke_width=0, font_family="Verdana", font_size="8"))
            if jour.weekday() == 0:
                vlines.add(svgwrite.text.Text('week:{0:02}'.format(jour.isocalendar()[1]), insert=((x*10+2)*mm, 6*mm), fill='black', stroke='black', stroke_width=0, font_family="Verdana", font_size="12"))
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
        self.reset_coord()

        if start is None:
            start_date = self.start_date()    
        else:
            start_date = start

        if end is None:
            end_date = self.end_date() 
        else:
            end_date = end + datetime.timedelta(days=1)


        maxx = (end_date - start_date).days 
        maxy = self.nb_elements()

        dwg = svgwrite.Drawing(filename, debug=True)
        dwg.add(self.svg_calendar(maxx, maxy, start_date, today))
    
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

        Keyword arguments:
        filename -- string, filename to save to
        today -- datetime.date of day marked as a reference
        start -- datetime.date of first day to draw
        end -- datetime.date of last day to draw
        ressources -- list of Ressource to check, default all
        """
        self.reset_coord()

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


        for t in self.get_tasks():
            t.check_conflict_between_task_and_ressources_vacations()



        dwg = svgwrite.Drawing(filename, debug=True)
        dwg.add(self.svg_calendar(maxx, maxy, start_date, today))
    
        nline = 1
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
                    while cday < t.end_date():
                        if cday in affected_days:
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
        return

    def start_date(self):
        """
        """
        first = self.tasks[0].start_date()
        for t in self.tasks:
            if t.start_date() < first:
                first = t.start_date()
        return first


    def end_date(self):
        """
        """
        last = self.tasks[0].end_date()
        for t in self.tasks:
            if t.end_date() > last:
                last = t.end_date()
        return last

    def svg(self, prev_y=0, start=None, end=None, color=None, level=0):
        """
        """
        if start is None:
            start = self.start_date()
        if end is None:
            end = self.end_date()
        if color is None or self.color is not None:
            color = self.color

        cy = prev_y
        prj = svgwrite.container.Group(id=self.name.replace(' ', '_'))
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
        svg = svgwrite.container.Group()
        for t in self.tasks:
            trepr = t.svg_dependencies(prj)
            if trepr is not None:
                svg.add(trepr)
        return svg


    def nb_elements(self):
        """
        """
        if self.cache_nb_elements is not None:
            return self.cache_nb_elements
        
        nb = 1
        for t in self.tasks:
            nb += t.nb_elements()

        self.cache_nb_elements = nb
        return nb 

    def reset_coord(self):
        """
        """
        self.cache_nb_elements = None
        for t in self.tasks:
            t.reset_coord()
        return

    def is_in_project(self, task):
        """
        """
        test = False
        for t in self.tasks:
            if t.is_in_project(task):
                return True
        return test


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
        for r in __flatten__(rlist):
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
        for r in __flatten__(tlist):
            if r not in flist:
                flist.append(r)
        return flist


# MAIN -------------------
if __name__ == '__main__':
    import doctest
    # non regression test
    doctest.testmod()
else:
    #__init_log_to_sysout__(level=logging.DEBUG)
    __init_log_to_sysout__(level=logging.WARNING)


#<EOF>######################################################################


