#!/usr/bin/env python
############################################################################
#
# MODULE:	g.search.data
# AUTHOR(S):	Jachym Cepicky <jachym.cepicky gmail.com>
# PURPOSE:	g.search.data in grass vector and raster maps using given keywords
# COPYRIGHT:	(C) 2015-2016 by the GRASS Development Team
#
#		This program is free software under the GNU General
#		Public License (>=v2). Read the file COPYING that
#		comes with GRASS for details.
#
#############################################################################

#%module
#% description: Search in GRASS database using given keywords
#% keyword: general
#% keyword: raster
#% keyword: vector
#% keyword: vector
#% keyword: search
#%end
#%option
#% key: keyword
#% multiple: yes
#% type: string
#% description: Keyword to be searched
#% required : yes
#%end
#%option
#% key: type
#% multiple: yes
#% type: string
#% required : no
#% description: Data type(s) (default: all)
#% options: raster,raster_3d,vector,all
#%end
#%flag
#% key: a
#% description: Display only modules where all keywords are available (AND), default: OR
#%end
#%flag
#% key: c
#% description: Use colorized (more readable) output to terminal
#%end
#%flag
#% key: g
#% description: Shell script format
#%end
#%flag
#% key: j
#% description: JSON format
#%end

import os
import sys

from grass.script.utils import diff_files, try_rmdir
from grass.exceptions import CalledModuleError
from grass.script import core as grass

COLORIZE=False

def main():
    global COLORIZE
    keywords = options['keyword'].lower().split(',')

    types = options['type']
    if not types:
        types = 'all'
    types = types.lower().split(',')
    if 'all' in types:
        types = ['raster', 'raster_3d', 'vector']


    AND = flags['a']
    out_format = None
    if flags['g']:
        out_format = 'shell'
    elif flags['j']:
        out_format = 'json'
    else:
        COLORIZE = flags['c']

    data = _search_data(keywords, AND, types)

    print data

    #print_results(modules, out_format) 

def check(keywords, data, AND):

    results = [False]
    if AND:
        results = len(keywords)*[False]

    for i in range(len(keywords)):
        keyword = keywords[i]
        if str(data).lower().find(keyword.lower()) > -1:
            if AND:
                results[i] = True
            else:
                results = [True]

    return not False in results

def _search_data(keywords, AND, types):

    results = {}

    for data_type in types:
        results[data_type] = _get_by_type(data_type)(keywords, AND)

    return results

def _search_map(keywords, AND, maptype, info_cmd, flags):

    result = []
    for mapfile in grass.parse_command('g.list', type=maptype):
        try:
            datas = grass.parse_command(info_cmd, map=mapfile, flags=flags)
            for param in datas:
                 if check(keywords, datas[param], AND):
                    result.append({
                        'name': mapfile,
                        'attributes': {
                            param: datas[param]
                        }
                    })
        except CalledModuleError as module_error:
            pass

    return result


def _search_raster(keywords, AND):
    return _search_map(keywords, AND, 'raster', 'r.info', 'e')

def _search_vector(keywords, AND):
    return _search_map(keywords, AND, 'vector', 'v.info', 'e')

def _search_raster_3d(keywords, AND):
    return _search_map(keywords, AND, 'raster_3d', 'r3.info', 'gh')

def _search_label(keywords, AND):
    return []

def _search_region(keywords, AND):
    return []

def _search_group(keywords, AND):
    return []
    
def _get_by_type(data_type):
    if data_type == 'raster':
        return _search_raster
    elif data_type == 'vector':
        return _search_vector
    elif data_type == 'raster_3d':
        return _search_raster_3d
    elif data_type == 'label':
        return _search_label
    elif data_type == 'region':
        return _search_region
    elif data_type == 'group':
        return _search_group

if __name__ == "__main__":
    options, flags = grass.parser()
    sys.exit(main())
