from xml.etree import ElementTree
import csv
# Парсим xml
tree = ElementTree.parse('input3.xml')
root = tree.getroot()

# Открываем csv
with open('output.csv', 'w') as f:

# Подбираем аттрибуты
    for child_of_root in root:
        docparams = child_of_root.attrib

# Вытаскиваем параметры
        for subchild in child_of_root.iter('СведНП'):
            name = subchild.attrib
        for subsubchild in child_of_root.iter('СведССЧР'):
            another = subsubchild.attrib

#Формируем конечный дикт
            result = dict(docparams)
            result.update(name)
            result.update(another)

#Закидываем дикт в csv
            w.writeheader()
            w = csv.DictWriter(f, result.keys())
            w.writerow(result)

#Пишем в консоль для отладки
            print (result)





