import sqlite3
import datetime
import logging
import os
import fnmatch
from contextlib import closing
from flask import Flask, request, render_template, g, flash, redirect, url_for, abort

DATABASE = 'rasp_db.db'
SECRET_KEY = 'development key'


FORMAT = '%(asctime)-15s %(thread)d %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, filename='log/myapp.log')
logger = logging.getLogger('app')


app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/photos')
def list_photos():
    files = []
    error = None
    for file in os.listdir('static/photos'):
        file = os.path.join('static/photos', file)
        if fnmatch.fnmatch(file, '*.jpg'):
            fs = os.stat(file)
            dt = datetime.datetime.fromtimestamp(fs.st_mtime)
            files.append((file, dt.strftime('%Y-%m-%d %H:%M')))
    files = sorted(files, key=lambda x: x[1])
    return render_template('list_photos.html', photos=files, error=error)

@app.route('/')
def rasp_sysset():
    error = None
    if request.method == 'POST':
        app.logger.debug('set sysset value')

    app.logger.debug('display sysset')
    cur = g.db.execute('select id, name, value from rasp_sysset order by id desc')
    rasp_sysset = [dict(id1=row[0], name=row[1], value=row[2]) for row in cur.fetchall()]
    app.logger.debug("rasp_sysset %r" % rasp_sysset)
    return render_template('rasp_sysset.html', sysset=rasp_sysset, error=error)

@app.route('/update', methods=['POST'])
def sysset_set_db():
    id1 = request.form.get('id1', None)
    value = request.form.get('value', None)

    if id1 == None or value == None:
        return abort(401)

    # sql_str = "update rasp_sysset set value = '%s' where id = %s " % (value, id1)

    g.db.execute("update rasp_sysset set value = ? where id = ?", [value, id1])
    g.db.commit()
    flash("Update successfully! id1='%s' value='%s'" % (id1, value))
    return redirect(url_for('rasp_sysset'))

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('init_table.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    app.logger.debug("connect db")
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        app.logger.debug("closing db")
        db.close()


if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0')
