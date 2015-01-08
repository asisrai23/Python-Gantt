#!/usr/bin/env python3
# -*- coding: utf-8-unix -*-
"""
org2gantt.py - version and date, see below

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
__version__ = '0.3.0'
__last_modification__ = '2015.01.08'


import datetime
import logging
import os
import sys
import re
import uuid

############################################################################

try:
    import clize
except ImportError:
    print("This program uses clize. See : https://github.com/epsy/clize")
    sys.exit(1)

############################################################################

try:
    import Orgnode
except ImportError:
    print("This program uses Orgnode. See : http://members.optusnet.com.au/~charles57/GTD/orgnode.html")
    sys.exit(1)

############################################################################

def __show_version__(name, **kwargs):
    """
    Show version
    """
    import os
    print("{0} version {1}".format(os.path.basename(name), __version__))
    return True


############################################################################

def _iso_date_to_datetime(isodate):
    """
    """
    __LOG__.debug("_iso_date_to_datetime ({0})".format({'isodate':isodate}))
    y, m, d = isodate.split('-')
    if m[0] == '0':
        m = m[1]
    if d[0] == '0':
        d = d[1]
    return "datetime.date({0}, {1}, {2})".format(y, m, d)

############################################################################

__LOG__ = None

############################################################################

def _init_log_to_sysout(level=logging.INFO):
    """
    """
    global __LOG__
    logger = logging.getLogger("org2gantt")
    logger.setLevel(level)
    fh = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    __LOG__ = logging.getLogger("org2gantt")
    return


############################################################################

@clize.clize(
    alias = {
        'org': ('o',),
        'debug': ('d',),
        'gantt': ('g',),
        },
    extra = (
        clize.make_flag(
            source=__show_version__,
            names=('version', 'v'),
            help="Show the version",
            ),
        )
    )
def __main__(org, gantt='', debug=False):
    """
    org2gantt.py
    
    org: org-mode filename

    gantt: output python-gantt filename (default sysout)
    
    debug: debug

    Example :
    python org2gantt.py TEST.org

    Written by : Alexandre Norman <norman at xael.org>
    """
    global __LOG__
    if debug:
        _init_log_to_sysout(logging.DEBUG)
    else:
        _init_log_to_sysout()

    if not os.path.isfile(org):
        __LOG__.error('** File do not exist : {0}'.format(org))
        sys.exit(1)
    
    # load orgfile
    nodes = Orgnode.makelist(org)

    __LOG__.debug('_analyse_nodes ({0})'.format({'nodes':nodes}))

    gantt_code = """#!/usr/bin/env python3
# -*- coding: utf-8-unix -*-

import datetime
import gantt
"""


    # Find CONFIGURATION in heading
    n_configuration = None
    for n in nodes:
        if n.headline == "CONFIGURATION":
            n_configuration = n

    planning_start_date = None
    planning_end_date = None
    planning_today_date = _iso_date_to_datetime(str(datetime.date.today()))
    bar_color = None
    one_line_for_tasks = False

    # Generate code for configuration
    if n_configuration is not None:
        if 'color' in n_configuration.properties:
            bar_color = n_configuration.properties['color']

        if 'one_line_for_tasks' in n_configuration.properties and n_configuration.properties['one_line_for_tasks'] == 't':
             one_line_for_tasks = True

        if 'start_date' in n_configuration.properties:
            # find date and use it
            dates = re.findall('[1-9][0-9]{3}-[0-9]{2}-[0-9]{2}', n_configuration.properties['start_date'])
            if len(dates) == 1:
                planning_start_date = _iso_date_to_datetime(dates[0])
            # find +1m
            elif n_configuration.properties['start_date'].startswith('-') or n_configuration.properties['start_date'].startswith('+'):
                sign = n_configuration.properties['start_date'][0]
                qte = int(n_configuration.properties['start_date'][1:-1])
                what = n_configuration.properties['start_date'][-1]

                sign = -1*(sign=='-') + 1*(sign=='+')
                if what == 'd':
                    planning_start_date = _iso_date_to_datetime(str(datetime.date.today() + datetime.timedelta(days=qte*sign)))
                elif what == 'w':
                    planning_start_date = _iso_date_to_datetime(str(datetime.date.today() + datetime.timedelta(weeks=qte*sign)))


        if 'end_date' in n_configuration.properties:
            # find date and use it
            dates = re.findall('[1-9][0-9]{3}-[0-9]{2}-[0-9]{2}', n_configuration.properties['end_date'])
            if len(dates) == 1:
                planning_end_date = _iso_date_to_datetime(dates[0])
            # find +1m
            elif n_configuration.properties['end_date'].startswith('-') or n_configuration.properties['end_date'].startswith('+'):
                sign = n_configuration.properties['end_date'][0]
                qte = int(n_configuration.properties['end_date'][1:-1])
                what = n_configuration.properties['end_date'][-1]

                sign = -1*(sign=='-') + 1*(sign=='+')
                if what == 'd':
                    planning_end_date = _iso_date_to_datetime(str(datetime.date.today() + datetime.timedelta(days=qte*sign)))
                elif what == 'w':
                    planning_end_date = _iso_date_to_datetime(str(datetime.date.today() + datetime.timedelta(weeks=qte*sign)))
                elif what == 'm':
                    planning_end_date = _iso_date_to_datetime(str(datetime.date.today() + datetime.timedelta(month=qte*sign)))
                elif what == 'y':
                    planning_end_date = _iso_date_to_datetime(str(datetime.date.today() + datetime.timedelta(years=qte*sign)))

        if 'today' in n_configuration.properties:
            dates = re.findall('[1-9][0-9]{3}-[0-9]{2}-[0-9]{2}', n_configuration.properties['today'])
            if len(dates) == 1:
                planning_today_date = _iso_date_to_datetime(dates[0])



    # Find RESOURCES in heading
    n_resources = []
    resources_id = []
    found = False
    plevel = 0
    for n in nodes:
        if found == True and n.level > plevel:
            n_resources.append(n)
        elif found == True and n.level <= plevel:
            break
        if found == False and n.headline == "RESOURCES":
            found = True
            plevel = n.level

    # Generate code for resources
    gantt_code += "\n#### Resources \n"
    next_level = 0
    current_level = 0
    current_group = None

    for nr in range(len(n_resources)):
        r = n_resources[nr]

        rname = r.headline
        rid = r.properties['resource_id'].strip()
        
        if rid in resources_id:
            __LOG__.critical('** Duplicate resource_id: [{0}]'.format(rid))
            sys.exit(1)

        resources_id.append(rid)

        if ' ' in rid:
            __LOG__.critical('** Space in resource_id: [{0}]'.format(rid))
            sys.exit(1)

        new_group_this_turn = False

        current_level = r.level
        if nr < len(n_resources) - 2:
            next_level = n_resources[nr+1].level

        # Group mode
        if current_level < next_level:
            gantt_code += "{0} = gantt.GroupOfResources('{1}')\n".format(rid, rname)
            current_group = rid
            new_group_this_turn = True
        # Resource
        else:
            gantt_code += "{0} = gantt.Resource('{1}')\n".format(rid, rname)
            
        # Vacations in body of node
        for line in r.body.split('\n'):
            if line.startswith('-'):
                dates = re.findall('[1-9][0-9]{3}-[0-9]{2}-[0-9]{2}', line)
                if len(dates) == 2:
                    start, end = dates
                    gantt_code += "{0}.add_vacations(dfrom={1}, dto={2})\n".format(rid, _iso_date_to_datetime(start), _iso_date_to_datetime(end))
                elif len(dates) == 1:
                    start = dates[0]
                    gantt_code += "{0}.add_vacations(dfrom={1})\n".format(rid, _iso_date_to_datetime(start))
                
            else:
                if line != '' and not line.startswith(':'):
                    __LOG__.warning("Unknown resource line : {0}".format(line))


        if new_group_this_turn == False and current_group is not None:
            gantt_code += "{0}.add_resource(resource={1})\n".format(current_group, rid)

            # end of group
            if current_level > next_level:
                current_group = None


    # Find VACATIONS in heading
    n_vacations = None
    for n in nodes:
        if n.headline == "VACATIONS":
            n_vacations = n

    # Generate code for vacations
    gantt_code += "\n#### Vacations \n"
    if n_vacations is not None:
        for line in n_vacations.body.split('\n'):
            if line.startswith('-'):
                dates = re.findall('[1-9][0-9]{3}-[0-9]{2}-[0-9]{2}', line)
                if len(dates) == 2:
                    start, end = dates
                    gantt_code += "gantt.add_vacations({0}, {1})\n".format(_iso_date_to_datetime(start), _iso_date_to_datetime(end))
                elif len(dates) == 1:
                    start = dates[0]
                    gantt_code += "gantt.add_vacations({0})\n".format(_iso_date_to_datetime(start))

            else:
                if line != '':
                    __LOG__.warning("Unknown vacation line : {0}".format(line))


    # Generate code for Projects
    gantt_code += "\n#### Projects \n"
    # Mother of all
    gantt_code += "project = gantt.Project(color='{0}')\n".format(bar_color)

    cproject = 0
    ctask = 0
    prj_found = False
    tasks_name = []
    # for inheriting project, ORDERED, color, resources
    prop_inherits = []
    prev_task = None
    for nr in range(len(nodes)):
        n = nodes[nr]

        __LOG__.debug('Analysing {0}'.format(n.headline))
        
        # it's a task / level 1
        if n.level == 1 \
               and  not n.headline in ('RESOURCES', 'VACATIONS', 'CONFIGURATION') \
               and 'no_gantt' not in n.tags \
               and n.todo in ('TODO', 'STARTED', 'HOLD', 'DONE', 'WAITING'):

            __LOG__.debug(' task / level 1')

            prop_inherits = []
            prj_found = False
            prj_found = True
            prev_task = None
            
            # Add task
            name, code = make_task_from_node(n)

            if name in tasks_name:
                __LOG__.critical("Duplicate task id: {0}".format(name))
                sys.exit(1)
            else:
                tasks_name.append(name)

            gantt_code += code
            gantt_code += "project.add_task(task_{0})\n".format(name)

        # new project heading
        # Not a task, it's a project
        # it should have children
        elif n.level >= 1 \
                 and  not n.headline in ('RESOURCES', 'VACATIONS', 'CONFIGURATION') \
                 and 'no_gantt' not in n.tags \
                 and not n.todo in ('TODO', 'STARTED', 'HOLD', 'DONE', 'WAITING'):

            if n.level == 1:
                prev_task = None
            

            if n.level > 1 and prj_found == False:
                __LOG__.debug(' do not keep')
                continue

            if len(prop_inherits) >= n.level:
                __LOG__.debug(' go one level up')
                prop_inherits = prop_inherits[:-1]


            __LOG__.debug(' new project heading')

            gantt_code += "###### Project {0} \n".format(n.headline)

            try:
                name = n.properties['task_id'].strip()
            except KeyError:
                name = str(uuid.uuid4()).replace('-', '_')
    

            __LOG__.debug('{0}'.format(prop_inherits))

            gantt_code += "project_{0} = gantt.Project(name='{1}', color='{2}')\n".format(name, n.headline, bar_color)
            try:
                gantt_code += "project_{0}.add_task(project_{1})\n".format(prop_inherits[-1]['project_id'], name)
            except KeyError:
                gantt_code += "project.add_task(project_{0})\n".format(name)
            except IndexError:
                gantt_code += "project.add_task(project_{0})\n".format(name)

            if n.level == 1:
                prop_inherits = []

            # Inherits ORDERED
            if 'ORDERED' in n.properties and n.properties['ORDERED'] == 't':
                ordered = True
            else:
                if len(prop_inherits) > 0:
                    ordered = prop_inherits[-1]['ordered']
                else:
                    prev_task = None
                    ordered = False

            # Inherits color            
            if 'color' in n.properties:
                color = n.properties['color']
            else:
                if len(prop_inherits) > 0:
                    color = prop_inherits[-1]['color']
                else:
                    color = None

    
            prop_inherits.append({'ordered':ordered, 'color':color, 'project_id':name})
            prj_found = True

        # It's a task
        elif n.level >= 1 \
                 and prj_found == True \
                 and  not n.headline in ('RESOURCES', 'VACATIONS', 'CONFIGURATION') \
                 and 'no_gantt' not in n.tags \
                 and n.todo in ('TODO', 'STARTED', 'HOLD', 'DONE', 'WAITING'):

            __LOG__.debug(' new task under project')

            if n.level == 1:
                prev_task = None
                


            if len(prop_inherits) >= n.level:
                __LOG__.debug(' go one level up')
                prop_inherits = prop_inherits[:-1]


            # Add task
            if len(prop_inherits) > 0:
                name, code = make_task_from_node(n, prop_inherits[-1], prev_task)
            else:
                name, code = make_task_from_node(n, [], prev_task)


            if name in tasks_name:
                __LOG__.critical("Duplicate task id: {0}".format(name))
                sys.exit(1)
            else:
                tasks_name.append(name)

            prev_task = name

            gantt_code += code
            #gantt_code += "project.add_task(task_{0})\n".format(name)

            try:
                gantt_code += "project_{0}.add_task(task_{1})\n".format(prop_inherits[-1]['project_id'], name)
            except KeyError:
                gantt_code += "project.add_task(task_{0})\n".format(name)
            except IndexError:
                gantt_code += "project.add_task(task_{0})\n".format(name)

        else:
            prj_found = False
            prop_inherits = []

            __LOG__.debug(' nothing')
            
            



    # Full project
    gantt_code += "\n#### Outputs \n"
    #gantt_code += "project_0 = gantt.Project(color='{0}')\n".format(bar_color)
    # for i in range(1, cproject + 1):
    #     gantt_code += "project_{0}.make_svg_for_tasks(filename='project_{0}.svg', today={1}, start={2}, end={3})\n".format(i, planning_today_date, planning_start_date, planning_end_date)
    #     gantt_code += "project_{0}.make_svg_for_resources(filename='project_{0}_resources.svg', today={1}, start={2}, end={3}, one_line_for_tasks={4})\n".format(i, planning_today_date, planning_start_date, planning_end_date, one_line_for_tasks)
        #gantt_code += "project_0.add_task(project_{0})\n".format(i)

    gantt_code += "project.make_svg_for_tasks(filename='project.svg', today={0}, start={1}, end={2})\n".format(planning_today_date, planning_start_date, planning_end_date)
    gantt_code += "project.make_svg_for_resources(filename='project_resources.svg', today={0}, start={1}, end={2}, one_line_for_tasks={3})\n".format(planning_today_date, planning_start_date, planning_end_date, one_line_for_tasks)



    # write Gantt code
    if gantt == '':
        print(gantt_code)
    else:
        open(gantt, 'w').write(gantt_code)




    __LOG__.debug("All done. Exiting.")
    
    return



############################################################################

def make_task_from_node(n, prop={}, prev_task=''):
    """
    """
    gantt_code = ""

    try:
        name = n.properties['task_id'].strip()
    except KeyError:
        name = str(uuid.uuid4()).replace('-', '_')
    
    if ' ' in name:
        __LOG__.critical('** Space in task_id: [{0}]'.format(name))
        sys.exit(1)
    
    fullname = n.headline
    start = end = duration = None
    if n.scheduled != '':
        start = "{0}".format(_iso_date_to_datetime(str(n.scheduled)))
    if n.deadline != '':
        end = "{0}".format(_iso_date_to_datetime(str(n.deadline)))
    if 'Effort' in n.properties:
        duration = n.properties['Effort'].replace('d', '')
    
    try:
        depends = n.properties['BLOCKER'].split()
    except KeyError:
        depends_of = None
    else: # no exception raised
        depends_of = []
        for d in depends:
            depends_of.append('task_{0}'.format(d))

    if 'ordered'in prop and prop['ordered'] and prev_task is not None and prev_task != '':
        depends_of = ['task_{0}'.format(prev_task)]

    
    try:
        percentdone = n.properties['PercentDone']
    except KeyError:
        percentdone = None
    
    if n.todo == 'DONE':
        if percentdone is not None:
            __LOG__.warning('** Task [{0}] marked as done but PercentDone is set to {1}'.format(name, percentdone))
        percentdone = 100
    
    # Resources as tag
    if len(n.tags) > 0:
        ress = "{0}".format(["{0}".format(x) for x in n.tags.keys()]).replace("'", "")
    # Resources as properties
    elif 'resource_id' in n.properties:
        ress = "{0}".format(["{0}".format(x) for x in n.properties['resource_id'].split()]).replace("'", "")
    else:
        ress = None


    # get color from task properties
    if 'color' in n.properties:
        color = "'{0}'".format(n.properties['color'])
    # inherits color if defined 
    elif 'color' in prop and prop['color'] is not None:
        color = "'{0}'".format(prop['color'])
    else:
        color = None

    
    gantt_code += "task_{0} = gantt.Task(name='{1}', start={2}, stop={6}, duration={3}, resources={4}, depends_of={5}, percent_done={7}, fullname='{8}', color={9})\n".format(name, name, start, duration, ress, str(depends_of).replace("'", ""), end, percentdone, fullname, color)
    
    
    return (name, gantt_code)

############################################################################




__all__ = ['org2gantt']


# MAIN -------------------
if __name__ == '__main__':

    clize.run(__main__)
    sys.exit(0)

    
#<EOF>######################################################################

