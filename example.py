from xml.etree import ElementTree

tree = ElementTree.parse('input3.xml')
root = tree.getroot()

for child_of_root in root:
    print (child_of_root.tag, child_of_root.attrib)

#for att in root:
 #   first = att.find('attval').text
 #   for subatt in att.find('children'):
 #       second = subatt.find('attval').text
 #       print('{},{}'.format(first, second))