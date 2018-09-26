from xml.etree import ElementTree
import csv

tree = ElementTree.parse('input3.xml')
root = tree.getroot()

with open('output.csv', 'w') as f:
    for child_of_root in root:
        docparams = child_of_root.attrib
        for subchild in child_of_root.iter('СведНП'):
            name = subchild.attrib
        for subsubchild in child_of_root.iter('СведССЧР'):
            another = subsubchild.attrib
            result = dict(docparams)
            result.update(name)
            result.update(another)
            w.writeheader()
            w = csv.DictWriter(f, result.keys())
            w.writerow(result)
            print (result)





