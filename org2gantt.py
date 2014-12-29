
import datetime
import logging
import sys

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
    
    # load orgfile
    nodes = Orgnode.makelist(org)

    # def _analyse_nodes(nodes, level):
    #     """
    #     """
    #     nl = []
    #     __LOG__.debug('_analyse_nodes ({0})'.format({'nodes':len(nodes), 'level':level}))
    #     sub_done = False
    #     for n in range(len(nodes)):
    #         if nodes[n].level == level:
    #             __LOG__.debug('same level {0}'.format(nodes[n].headline))
    #             nl.append(nodes[n])
    #             sub_done = False
    #         elif nodes[n].level > level and sub_done == False:
    #             __LOG__.debug('sub level {0}'.format(nodes[n].headline))
    #             sub_done = True
    #             nl.append(_analyse_nodes(nodes[n:], nodes[n].level))
    #         elif nodes[n].level < level:
    #             __LOG__.debug('sup level {0}'.format(nodes[n].headline))
    #             sub_done = False
    #             return nl
    #     return nl

    __LOG__.debug('_analyse_nodes ({0})'.format({'nodes':nodes}))

    # Analyse nodes
    #list_nodes = _analyse_nodes(nodes, 1)
 
    gantt_code = """import datetime
import gantt
"""


    # Find RESSOURCES in heading
    n_ressources = []
    found = False
    plevel = 0
    for n in nodes:
        if found == True and plevel == n.level:
            n_ressources.append(n)
        elif found == True and plevel != n.level:
            break
        if n.headline == "RESSOURCES":
            found = True
            plevel = n.level+1



    # Generate code for ressources
    gantt_code += "\n#### Ressources \n"
    for r in n_ressources:
        gantt_code += "r{0} = gantt.Ressource('{0}')\n".format(r.headline)
        for line in r.body.split('\n'):
            if '--' in line:
                start = line.split('--')[0].split('[')[1].split(' ')[0]
                end = line.split('--')[1].split('[')[1].split(' ')[0]
                gantt_code += "r{0}.add_vacations(dfrom={1}, dto={2})\n".format(r.headline, _iso_date_to_datetime(start), _iso_date_to_datetime(end))
            else:
                if line != '':
                    print('ERR',line)


    # Find VACATIONS in heading
    n_vacations = None
    for n in nodes:
        if n.headline == "VACATIONS":
            n_vacations = n

    # Generate code for vacations
    gantt_code += "\n#### Vacations \n"
    if n_vacations is not None:
        for line in n_vacations.body.split('\n'):
            if '--' in line:
                start = line.split('--')[0].split('[')[1].split(' ')[0]
                end = line.split('--')[1].split('[')[1].split(' ')[0]
                exec("sd = " + _iso_date_to_datetime(start))
                exec("en = " + _iso_date_to_datetime(end))

                while sd <= en:               
                    gantt_code += "gantt.add_vacations({0})\n".format(_iso_date_to_datetime(str(sd)))
                    sd += datetime.timedelta(days=1)
            else:
                print(line)


    # Generate code for Projects
    gantt_code += "\n#### Projects \n"
    cproject = 0
    ctask = 0
    prj_found = False
    tasks_name = {}
    for n in nodes:
        # new project heading
        if n.level == 1 and  not n.headline in ('RESSOURCES', 'VACATIONS') and 'no_gantt' not in n.tags:
            cproject += 1
            gantt_code += "###### Project {0} \n".format(n.headline)
            gantt_code += "project_{0} = gantt.Project(name='{1}')\n".format(cproject, n.headline)
            prj_found = True
        elif n.level == 1:
            prj_found = False
        elif n.level > 1 and prj_found == True and n.todo in ('TODO', 'STARTED', 'HOLD'):
            ctask += 1
            name = n.headline
            start = "{0}".format(_iso_date_to_datetime(str(n.scheduled)))
            duration = n.properties['Effort'].replace('d', '')

            try:
                depends = n.properties['Depends'].split(';')
            except KeyError:
                depends_of = None
            else: # no exception raised
                depends_of = []
                for d in depends:
                    depends_of.append(tasks_name[d])

            if len(n.tags) > 0:
                ress = "{0}".format(["r{0}".format(x) for x in n.tags.keys()]).replace("'", "")
            else:
                ress = None
            gantt_code += "task_{0} = gantt.Task(name='{1}', start={2}, duration={3}, ressources={4}, depends_of={5})\n".format(ctask, name, start, duration, ress, str(depends_of).replace("'", ""))
            if name in tasks_name:
                __LOG__.error("Duplicate task name : {0}".format(name))

            tasks_name["{0}".format(name)] = "task_{0}".format(ctask)
            gantt_code += "project_{0}.add_task(task_{1})\n".format(cproject, ctask)
            #p1.add_task(t1)


    gantt_code += "\n#### Outputs \n"
    gantt_code += "project_0 = gantt.Project()\n"
    for i in range(1, cproject + 1):
        gantt_code += "project_{0}.make_svg_for_tasks(filename='project_{0}.svg', today={1})\n".format(i, _iso_date_to_datetime(str(datetime.date.today())))
        gantt_code += "project_{0}.make_svg_for_ressources(filename='project_{0}_ressources.svg', today={1})\n".format(i, _iso_date_to_datetime(str(datetime.date.today())))
        gantt_code += "project_0.add_task(project_{0})\n".format(i)

    gantt_code += "project_0.make_svg_for_tasks(filename='project.svg', today={0})\n".format(_iso_date_to_datetime(str(datetime.date.today())))
    gantt_code += "project_0.make_svg_for_ressources(filename='project_ressources.svg', today={0})\n".format(_iso_date_to_datetime(str(datetime.date.today())))



    # write Gantt code
    if gantt == '':
        print(gantt_code)
    else:
        open(gantt, 'w').write(gantt_code)







    __LOG__.debug("All done. Exiting.")
    
    return

############################################################################




__all__ = ['org2gantt']


# MAIN -------------------
if __name__ == '__main__':

    clize.run(__main__)
    sys.exit(0)

    
#<EOF>######################################################################

