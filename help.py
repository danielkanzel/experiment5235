import os

import xml.etree.cElementTree as ET

XML_FILE = os.path.join(os.environ['HOME'], 'input2.xml')

try:
    tree = ET.ElementTree(file=XML_FILE)
    print(help(tree))
except IOError as e:
    print('nERROR - cant find file: %sn' % e)
