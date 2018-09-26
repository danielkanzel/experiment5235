from xml.etree import ElementTree

tree = ElementTree.parse('input3.xml')
root = tree.getroot()

for child_of_root in root:
    docparams = child_of_root.attrib
    for subchild in child_of_root.iter('СведНП'):
        name = subchild.attrib
    for subsubchild in child_of_root.iter('СведССЧР'):
        another = subsubchild.attrib
        result = dict(docparams)
        result.update(name)
        result.update(another)
        print(result)

#for att in root:
 #   first = att.find('attval').text
 #   for subatt in att.find('children'):
 #       second = subatt.find('attval').text
 #       print('{},{}'.format(first, second))