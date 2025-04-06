

### Scenario: One field from hello.py was renamed. Migrate only can create a new database table column of that new name. (from class role-table roles, field 'name' -> 'rolename'
### Therefore, we must synchronise data from the old to the new-named column 


import json
import sqlite3
    # SELECT FROM roles WHERE
    # INSERT OR IGNORE INTO roles (column_a,column_b) VALUES (?, ?), (a_val, b_val)
#from hello import db
#from hello import User,Role


# str_data = open(fname).read()
# json_data = json.loads(str_data)
# for entry in json_data:


### Route 1
conn = sqlite3.connect('data.sqlite')
cur = conn.cursor()

def syncdata():
    i = 1
    while True:
        try:
            cur.execute('''SELECT name FROM roles WHERE id=?''', (i,))
            rolename_value = cur.fetchone()[0]   ### not 'cur.fetchone()'
            if rolename_value != None:
                #cur.execute('''INSERT OR IGNORE INTO roles (rolename) VALUES (?)''', (rolename_value,))
                #cur.execute('''INSERT INTO roles (rolename) VALUES (?)''', (rolename_value,))
                cur.execute('''INSERT OR REPLACE INTO roles (rolename) VALUES (?)''', (rolename_value,))
                conn.commit()
                print('Successfully synchronised ' + rolename_value)
        except TypeError:
            break
        i += 1
        continue
    print('Synchronisation done.')
