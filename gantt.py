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

Contributors :
 - Jean-Lou Schmidt
 - Olivier Singer

Documentation :
 - EM630100UT68548.pdf [CONTROL-M/Enterprise Manager - Utility Guide]
   p33 
 - MVS63010PR63689.pdf [CONTROL-M/Job Parameter and Variable Reference Guide]
   p205
"""

__author__ = 'Alexandre Norman (norman at xael.org)'
__version__ = '0.1.0'
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

WORKED_DAY = [0, 1, 2, 3 ,4]
HOLLIDAYS = [
    datetime.date(2014, 12, 25),
    datetime.date(2015, 1, 1),
    ]

############################################################################

def __init_log_to_sysout__(level=logging.INFO):
    """
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


class Task(object):
    """
    """
    def __init__(self, name, start=None, stop=None, duration=None, depends_of=None, ressource=None, percent_done=0):
        """
        """
        __LOG__.debug('** Task::__init__ {0}'.format({'name':name, 'start':start, 'stop':stop, 'duration':duration, 'depends_of':depends_of, 'ressource':ressource, 'percent_done':percent_done}))
        self.name = name
        self.start = start
        self.duration = duration - 1
        self.depends_of = depends_of
        self.ressource = ressource
        self.percent_done = percent_done
        return


    def start_date(self):
        """
        """
        #__LOG__.debug('** Task::start_date ({0})'.format(self.name))
        if self.depends_of is None:
            #__LOG__.debug('*** Do not depend of other task')
            start = self.start
            while start.weekday() not in WORKED_DAY or start in HOLLIDAYS:
                start = start + datetime.timedelta(days=1)
            return start
        else:
            if type(self.depends_of) is type([]):
                #__LOG__.debug('*** Do depend of other tasks')
                prev_task_end = self.depends_of[0].end_date() + datetime.timedelta(days=1)
                for t in self.depends_of:
                    if t.end_date() > prev_task_end:
                        #__LOG__.debug('*** latest one {0} which end on {1}'.format(t.name, t.end_date()))
                        prev_task_end = t.end_date() + datetime.timedelta(days=1)
                if prev_task_end > self.start:
                    return prev_task_end
                else:
                    start = self.start
                    while start.weekday() not in WORKED_DAY or start in HOLLIDAYS:
                        start = start + datetime.timedelta(days=1)
                    return start
            else:
                #__LOG__.debug('*** Do depend of one task ({0}) which end on {1}'.format(self.depends_of.name, self.depends_of.end_date()))
                prev_task_end = self.depends_of.end_date() + datetime.timedelta(days=1)
                if prev_task_end > self.start:
                    return prev_task_end
                else:
                    start = self.start
                    while start.weekday() not in WORKED_DAY or start in HOLLIDAYS:
                        start = start + datetime.timedelta(days=1)
                    return start


    def end_date(self):
        """
        """
        __LOG__.debug('** Task::end_date ({0})'.format(self.name))
        current_day = self.start_date()
        real_duration = 0
        duration = self.duration
        while duration > 0:
            if current_day.weekday() in WORKED_DAY and current_day not in HOLLIDAYS:
                __LOG__.debug('*** day worked {0}'.format(current_day.weekday()))
                real_duration = real_duration + 1
                duration -= 1
            else:
                __LOG__.debug('*** day not worked {0}'.format(current_day.weekday()))
                real_duration = real_duration + 1

            current_day = self.start_date() + datetime.timedelta(days=real_duration)
            
        return self.start_date() + datetime.timedelta(days=real_duration)


    def svg(self, prev_y=0, start=None, end=None, color='#FFFF90', level=None):
        """
        """
        if start is None:
            start = self.start_date()
        if end is None:
            end = self.end_date()

        __LOG__.warning("{0}".format(self.start_date()))
        __LOG__.warning("{0}".format(start))
        __LOG__.warning("{0}".format((self.start_date() - start).days))
        x = (self.start_date() - start).days * 10
        y = prev_y * 10
        d = (self.end_date() - self.start_date()).days * 10
        svg = svgwrite.container.Group(id=self.name.replace(' ', '_'))
        bar = svgwrite.shapes.Rect(
            insert=((x+1)*mm, (y+1)*mm),
            size=((d-2)*mm, 8*mm),
            fill=color,
            stroke=color,
            stroke_width=1,
            )
        svg.add(bar)
        if self.percent_done > 0:
            barshade = svgwrite.shapes.Rect(
                insert=((x+1)*mm, (y+6)*mm),
                size=(((d-2)*self.percent_done/100)*mm, 3*mm),
                fill="#000000",
                stroke=color,
                stroke_width=1,
                opacity=0.3,
                )
            svg.add(barshade)

        svg.add(svgwrite.text.Text(self.name, insert=((x+2)*mm, (y + 5)*mm), fill='black', stroke='black', stroke_width=0, font_family="Verdana", font_size="15"))

        if self.ressource is not None:
            svg.add(svgwrite.text.Text(self.ressource, insert=((x+2)*mm, (y + 8.5)*mm), fill='purple', stroke='black', stroke_width=0, font_family="Verdana", font_size="10"))


        return (svg, 1)


    def nb_elements(self):
        """
        """
        return 1


class Project(object):
    """
    """
    def __init__(self, name="", color='#FFFF90'):
        """
        """
        self.tasks = []
        self.name = name
        self.color = color
        return

    def add_task(self, task):
        """
        """
        self.tasks.append(task)
        return

    def make_svg_for_tasks(self, filename, today=None):
        """
        """
        dwg = svgwrite.Drawing(filename, debug=True)
    
        maxx = (p.end_date()-p.start_date()).days
        maxy = p.nb_elements()
    
        start_date = p.start_date()
    
        vlines = dwg.add(dwg.g(id='vlines', stroke='lightgray'))
        for x in range(maxx+1):
            vlines.add(dwg.line(start=(x*cm, 1*cm), end=(x*cm, (maxy+1)*cm)))
            if not (start_date + datetime.timedelta(days=x)).weekday() in WORKED_DAY or (start_date + datetime.timedelta(days=x)) in HOLLIDAYS:
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
            vlines.add(svgwrite.text.Text('{0:02}/{1:02}'.format(jour.day, jour.month), insert=((x*10+2)*mm, 9*mm), fill='black', stroke='black', stroke_width=0, font_family="Verdana", font_size="8"))
            if jour.weekday() == 0:
                vlines.add(svgwrite.text.Text('week:{0:02}'.format(jour.isocalendar()[1]), insert=((x*10+2)*mm, 6*mm), fill='black', stroke='black', stroke_width=0, font_family="Verdana", font_size="12"))


        hlines = dwg.add(dwg.g(id='hlines', stroke='lightgray'))
        for y in range(1, maxy+2):
            hlines.add(dwg.line(start=(0*cm, y*cm), end=((maxx+1)*cm, y*cm)))
    
        
        psvg, pheight = p.svg(prev_y=1, color = self.color)
        dwg.add(psvg)
        dwg.save()
        return

    def make_svg_for_ressources(self, ressources=None):
        """
        """
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
        prj.add(svgwrite.text.Text('{0}'.format(self.name), insert=(6*(level+1)*mm, (cy*10+7)*mm), fill='black', stroke='white', stroke_width=0, font_family="Verdana", font_size="18"))

        prj.add(svgwrite.shapes.Rect(
            insert=(7*(level)*mm, (cy+0.5)*cm),
            size=(0.2*cm, (self.nb_elements()-1)*cm),
            fill='purple',
            stroke='lightgray',
            stroke_width=0,
            opacity=0.5
            ))

        cy += 1
        
        for t in self.tasks:
            trepr, theight = t.svg(cy, start=start, end=end, color=color, level=level+1)
            prj.add(trepr)
            cy += theight
            
        return (prj, cy-prev_y)

    def nb_elements(self):
        """
        """
        nb = 1
        for t in self.tasks:
            nb += t.nb_elements()
        return nb 




if __name__ == '__main__':
    #basic_shapes('basic_shapes.svg')
    __init_log_to_sysout__(level=logging.DEBUG)
    __init_log_to_sysout__(level=logging.WARNING)
    t1 = Task(name='tache1', start=datetime.date(2014, 12, 25), duration=4, percent_done=44, ressource="Alexandre")
    t1b = Task(name='tache1b', start=datetime.date(2014, 12, 29), duration=3)
    t2 = Task(name='tache2', start=datetime.date(2014, 12, 28), duration=6)
    t3 = Task(name='tache3', start=datetime.date(2014, 12, 25), duration=40, depends_of=[t1, t1b, t2])
    t3b = Task(name='tache3b', start=datetime.date(2014, 12, 25), duration=4, depends_of=t1b)
    t4 = Task(name='tache4', start=datetime.date(2015, 01, 01), duration=4, depends_of=t1)

    print('t1', t1.start_date(), t1.end_date())
    print('t1b', t1b.start_date(), t1b.end_date())
    print('t2', t2.start_date(), t2.end_date())
    print('t3', t3.start_date(), t3.end_date())
    print('t4', t4.start_date(), t4.end_date())


    p1 = Project(name='Projet 1')
    p1.add_task(t1)
    p1.add_task(t1b)
    p1.add_task(t2)
    p1.add_task(t3)
    p1.add_task(t4)



    p2 = Project(name='Projet 2', color='#FFFF40')
    p2.add_task(t1)
    p2.add_task(t2)

    p = Project(name='Gantt')
    p.add_task(p1)
    p.add_task(p2)
    p.add_task(t3b)


    print p1.nb_elements()
    print p2.nb_elements()
    print p.nb_elements()


    print('p1', p1.start_date(), p1.end_date())
    print('p2', p2.start_date(), p2.end_date())
    print('p', p.start_date(), p.end_date())

##########################$ MAKE DRAW ###############
    p.make_svg_for_tasks(filename='/tmp/test.svg', today=datetime.date(2014, 12, 31))
##########################$ MAKE DRAW ###############

    
# BOUTEILLE
