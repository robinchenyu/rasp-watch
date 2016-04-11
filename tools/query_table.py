import sqlite3
conn = sqlite3.connect('rasp_db.db')

c = conn.cursor()



# # Insert a row of data
# c.execute("""insert into stocks
#           values ('2006-01-05','BUY','RHAT',100,35.14)""")

# # Save (commit) the changes
# conn.commit()

c.execute('''select * from rasp_sysset''')
for row in c:
    id, name, val = row
    print("%s => %s" % (name, val))

# We can also close the cursor if we are done with it
c.close()
