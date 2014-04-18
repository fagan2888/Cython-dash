"""
    Generate Dash docset for Data Structure wikibooks
"""
import sqlite3
import os
import urllib
import urllib2
from bs4 import BeautifulSoup as bs
import requests


# CONFIGURATION
docset_name = 'cython.docset'
output = docset_name + '/Contents/Resources/Documents'
root_url = 'http://docs.cython.org'


# create docset directory
docpath = output + '/'
if not os.path.exists(docpath): os.makedirs(docpath)

# soup
data = requests.get(root_url).text
soup = bs(data)
open(os.path.join(output, 'index.html'), 'wb').write(data.encode('ascii', 'ignore'))
# add icon
icon = 'http://numfocus.org/images/cython.png'
urllib.urlretrieve(icon, docset_name + "/icon.png")


def update_db(name, path):
    typ = 'func'
    cur.execute("SELECT rowid FROM searchIndex WHERE path = ?", (path,))
    fetched = cur.fetchone()
    if fetched is None:
        cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, typ, path))
        print('DB add >> name: %s, type: %s,  path: %s' % (name, typ, path))
    else:
        print("record exists")


def add_docs():
    sections = []
    titles = []
    for i, link in enumerate(soup.findAll('a')):
        name = link.text.strip()
        path = link.get('href')

        if path is not None and not path.startswith('http://') and not path.startswith('https://'):
            update_db(name, path)



def add_infoplist():
    name = docset_name.split('.')[0]
    info = " <?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
           "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\"> " \
           "<plist version=\"1.0\"> " \
           "<dict> " \
           "    <key>CFBundleIdentifier</key> " \
           "    <string>{0}</string> " \
           "    <key>CFBundleName</key> " \
           "    <string>{1}</string>" \
           "    <key>DocSetPlatformFamily</key>" \
           "    <string>{2}</string>" \
           "    <key>isDashDocset</key>" \
           "    <true/>" \
           "    <key>dashIndexFilePath</key>" \
           "    <string>index.html</string>" \
           "</dict>" \
           "</plist>".format(name, name, name)
    open(docset_name + '/Contents/info.plist', 'wb').write(info)


if __name__ == '__main__':

    db = sqlite3.connect(docset_name + '/Contents/Resources/docSet.dsidx')
    cur = db.cursor()
    try:
        cur.execute('DROP TABLE searchIndex;')
    except:
        pass
    cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
    cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

    # start
    add_docs()
    add_infoplist()

    # commit and close db
    db.commit()
    db.close()