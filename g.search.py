#!/usr/bin/env python
############################################################################
#
# MODULE:	g.search
# AUTHOR(S):	Jachym Cepicky <jachym.cepicky gmail.com>
# PURPOSE:	g.search in grass modules using keywords
# COPYRIGHT:	(C) 2015-2016 by the GRASS Development Team
#
#		This program is free software under the GNU General
#		Public License (>=v2). Read the file COPYING that
#		comes with GRASS for details.
#
#############################################################################

#%module
#% description: Search in GRASS modules using keywords
#% keyword: general
#% keyword: modules
#% keyword: search
#%end
#%option
#% key: keyword
#% multiple: yes
#% type: string
#% description: Keyword to be searched
#% required : yes
#%end
#%flag
#% key: a
#% description: Display only modules where all keywords are available
#% guisection: All keywords
#%end

import os
import sys

from grass.script.utils import diff_files, try_rmdir
from grass.script import core as grass

try:
    import xml.etree.ElementTree   as etree
except ImportError:
    import elementtree.ElementTree as etree # Python <= 2.4

def main():
    keywords = options['keyword'].lower().split(',')
    allkws = flags['a']

    WXGUIDIR = os.path.join(os.getenv("GISBASE"), "gui", "wxpython")
    filename = os.path.join(WXGUIDIR, 'xml', 'module_items.xml')
    menudata_file = open(filename, 'r')

    menudata = etree.parse(menudata_file)
    menudata_file.close()

    items = menudata.findall('module-item')
    for item in items:
        name = item.attrib['name']
        description = item.find('description').text
        module_keywords = item.find('keywords').text

        found = [False]
        if allkws:
            found = [False] * len(keywords)

        for idx in range(len(keywords)):
            keyword = keywords[idx]
            if name.lower().find(keyword) > -1 or\
               description.lower().find(keyword) > -1 or\
               module_keywords.lower().find(keyword) > -1:

                if allkws:
                    found[idx] = True
                else:
                    found = [True] * len(keywords)
                    break

        if False not in found:
            print """
{}
\tDescription: {}
\tKeywords: {}""".format(name, description, module_keywords)


if __name__ == "__main__":
    options, flags = grass.parser()
    sys.exit(main())
