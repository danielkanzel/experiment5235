from xml.etree import ElementTree
import os
import psycopg2
import urllib.request
import zipfile
import traceback
import sys
import logging

LOGGER = None
def setup_logger():
    logger = logging.getLogger('nalog_loader')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


URL = 'http://data.nalog.ru/opendata/7707329152-sshr/data-20180801-structure-20180801.zip'

Q_INSERT = """
INSERT INTO nalog.data (%s) VALUES %s;
"""

Q_DELETE = """
DELETE FROM nalog.data (%s) values %s;
"""


def download_datafile(URL):
    LOGGER.info("download loaded file %s" % URL)
    with urllib.request.urlopen(URL) as response:
            with open('data.zip', 'wb') as datafile:
                for i in iter(lambda: response.read(4096), b''):
                    datafile.write(i)

def extract_datafile():
    LOGGER.info("extract file")
    if os.path.exists('files'):
        for i in os.listdir('files'):
            os.unlink(os.path.join('files',i))
    else:
        os.mkdir('files')

    with zipfile.ZipFile('data.zip') as zipdata:
        zipdata.extractall(path='files')

class Database:
    def __init__(self, dbname='load_from_nalog', user='bpolozov'):
        self.c = psycopg2.connect(f'dbname={dbname} user={user}')
        
    def create_database(self):
        with self.c.cursor() as cur:
            LOGGER.info("creating DDL")
            cur.execute("""
                CREATE SCHEMA IF NOT EXISTS nalog
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS nalog.data 
            (
                filename text,
                ИдДок uuid, 
                ДатаДок date, 
                ДатаСост date, 
                НаимОрг text, 
                ИННЮЛ text, 
                КолРаб int
            )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS nalog.files
                (
                filename text PRIMARY KEY,
                loaded bool,
                failed bool
                )
            """)
            self.c.commit()
            
    def file_insert_new(self,filename):
        LOGGER.info("insert new file %s" % filename)
        with self.c.cursor() as cur:
            cur.execute("""
                INSERT INTO nalog.files (filename, loaded, failed) VALUES ('%s', 'f', 'f')
            """ % filename
            )
            self.c.commit()
    
    def file_set_failed(self,filename):
        LOGGER.info("set failed file %s" % filename)
        with self.c.cursor() as cur:
            cur.execute("""
                UPDATE nalog.files SET failed = 't' WHERE filename = '%s'
            """ % filename
            )
            self.c.commit()
            
    def file_set_loaded(self, filename):
        LOGGER.info("set loaded file %s" % filename)
        with self.c.cursor() as cur:
            cur.execute("""
                UPDATE nalog.files SET loaded = 't' WHERE filename = '%s'
            """ % filename
            )
            self.c.commit()
    
    def data_insert(self, query):
        with self.c.cursor() as cur:
            cur.execute(query)
            self.c.commit()
            res = cur.rowcount
            return res
    
        
                


def make_query(filename):
    LOGGER.info("make query for file %s" % filename)
    # Парсим xml
    tree = ElementTree.parse(os.path.join('files',filename))
    root = tree.getroot()
    data = []
    header = None
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
            if not header:
                header = [x for x in result.keys()]
            data.append([x for x in result.values()])
    
    header.insert(0, 'filename')
    for i in data:
        i.insert(0,filename)

    # TODO: regexp for checking if strings is valid
    data = ', '.join(["('%s', '%s', '%s', '%s', '%s', '%s', %s)" % tuple([i.replace("'","''") for i in x]) if len(x) == 7 else print(x) for x in data])

        

    return Q_INSERT % (', '.join(header), data)

def make_query_cleanup(filename):
    pass

def insert_to_database(filename, c):
    LOGGER.info("insert_to_database called file %s" % filename)
    query = None
    res = None
    try:
        query = make_query(filename)
        c.file_insert_new(filename)
    except Exception as e:
        print_exception(sys.exc_info())
        c.file_set_failed(filename)
    if query:
        try:
            res = c.data_insert(query)
            if res:
                c.file_set_loaded(filename)
        except Exception as e:
            print_exception(sys.exc_info())
            c.file_set_failed(filename)
    else:
        LOGGER.error("query creating failed %s" % filename)
    
        
        
            
if __name__ == '__main__':
    LOGGER = setup_logger()
    c = Database()
    if len(sys.argv) > 1:
        if sys.argv[1] == 'init_db':
            c.create_database()
            sys.exit(0)

    #download_datafile(URL)
    #extract_datafile()
    for filename in os.listdir('files'):
        insert_to_database(filename, c)
    
    
