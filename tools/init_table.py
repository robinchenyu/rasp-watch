import sqlite3
conn = sqlite3.connect('rasp_db.db')

c = conn.cursor()

# # Create table
# c.execute('''create table stocks
# (date text, trans text, symbol text,
#  qty real, price real)''')
try:
    c.execute('''
        drop table rasp_sysset
        ''')
except Exception as e:
    print(str(e))
c.execute(''' 
    create table rasp_sysset (
      id integer primary key autoincrement,
      name text not null,
      value text not null
    )
     ''')

c.execute('''
    insert into rasp_sysset
    values (1, 'start_time', '08:00')
    ''')
c.execute('''
    insert into rasp_sysset
    values (2, 'end_time', '22:00')
    ''')
c.execute('''
    insert into rasp_sysset
    values (3, 'camera_delay', '5')
    ''')


# # Insert a row of data
# c.execute("""insert into stocks
#           values ('2006-01-05','BUY','RHAT',100,35.14)""")

# # Save (commit) the changes
conn.commit()

c.execute('''select * from rasp_sysset''')
for row in c:
    id, name, val = row
    print("%s => %s" % (name, val))

# We can also close the cursor if we are done with it
c.close()
