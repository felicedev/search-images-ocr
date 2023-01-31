import os
import glob
import sqlite3
import pytesseract
from PIL import Image

DB_FILENAME = 'ocr.db'
PATTERN_IMAGE_SEARCH = 'images/**/*.png'


def create_db():
    sqlite3.connect(DB_FILENAME)


def get_db():
    con = sqlite3.connect(DB_FILENAME)
    cur = con.cursor()
    return con, cur

def exists_table(cur):
    res = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ImageText'")
    return len(res.fetchall()) == 1

def table_is_not_empty(cur):
    res = cur.execute("SELECT * FROM ImageText")
    return len(res.fetchall()) > 0

def insert(con, cur, filename, ocr_text):
    data = (filename, ocr_text)
    cur.execute(f"INSERT INTO ImageText VALUES(?,?)", data)
    con.commit()


def insert_images(con, cur, pattern):
    files = glob.glob(pattern, recursive=True)
    n = len(files)
    c = 0
    print(f'Files to be scanned: {n}')
    for file in files:
        ocr_text = pytesseract.image_to_string(Image.open(file))
        ocr_text = ocr_text.strip()
        insert(con, cur, file, ocr_text)
        c = c + 1
        print(f'Files inserted {c}/{n}')


def search(cur, prompt):
    result = select_all(cur)
    match = [x for x in result if prompt in x[1]]

    if not match:
        return None
    el = match[0][0]
    return el


def select_all(cur):
    res = cur.execute("SELECT * FROM ImageText")
    return res.fetchall()


def search_show_image(cur, prompt):
    if not prompt:
        print("Nessun risultato\n")
        return

    el = search(cur, prompt)

    if el:
        im = Image.open(el)
        im.show()
    else:
        print('No result found')


if not os.path.isfile(DB_FILENAME):
    create_db()

con, cur = get_db()

if not exists_table(cur):
    cur.execute("CREATE TABLE ImageText(filename TEXT, ocr TEXT)")

if not table_is_not_empty(cur):
    insert_images(con, cur, PATTERN_IMAGE_SEARCH)

while True:
    print("Type prompt to search: ")
    prompt = input()
    search_show_image(cur, prompt)