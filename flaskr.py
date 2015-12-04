#all the imports
import sqlite3
import time
import datetime 
import hashlib
from flask import Flask,request,session,g,redirect,url_for,abort,render_template,flash
from contextlib import closing



#create our little appliaction:)
app = Flask(__name__)

app.config.from_pyfile('config.py')


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql',mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def  teardowm_request(exception):
    db = getattr(g,'db',None)
    if db is not None:
        db.close()
    g.db.close()



@app.route('/')
def show_entries():
    #cur = g.db.execute('select title,text from entries order by id desc')
    #entries = [dict(title=row[0],text=row[1]) for row in cur.fetchall()]
    #return render_template('show_entries.html',entries=entries)
    return render_template('add_task.html')

@app.route('/add',methods=['POST','GET'])
def addEntry():
    session.pop('viewTasks',None)
    if not session.get('logged_in'):
        abort(401)
    if request.method =='POST': 
        userid = session.get('userid')
        g.db.execute('insert into tasks(taskname,taskdescr,createby,createtime) values(?,?,?,?)',[request.form['title'],request.form['text'],userid,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        g.db.commit()
        flash('New task was successfully added!')
        return redirect(url_for('show_entries'))
    return redirect(url_for('show_entries'))

@app.route('/signin',methods=['POST','GET'])
def sign():
    error = None
    if request.method =='POST': 
        m = hashlib.md5()
        m.update(request.form['password'])
        pw = m.hexdigest()
        print pw
        g.db.execute('insert into user(username,password,reg_time) values(?,?,?)',[request.form['username'],pw,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        g.db.commit()
        flash('signin successfully')
        return redirect(url_for('show_entries'))
    return render_template('sign.html',error=error)

@app.route('/login',methods=['GET','POST'])
def login():
    error = None
    if request.method =='POST':
        cur = g.db.cursor()
        cur.execute("select password,userid from user where username='%s'"%(request.form['username']))
        name = request.form['username']
        rows = cur.fetchall()
        if not rows:
            error = 'Invalid username or Invalid password'
        elif hashlib.md5(request.form['password']).hexdigest() !=rows[0][0]:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            session['userid'] = rows[0][1]
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html',error=error)



@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    session.pop('viewTasks',None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/viewMyTasks',methods=['GET','POST'])
def viewMyTasks():
    if not session.get('logged_in'):
        abort(401)
    userid = session.get('userid')
    session['viewTasks'] = True
    cur = g.db.execute("select taskname,taskdescr from tasks where createby='%s' order by createtime desc"%userid)
    tasks = [dict(taskname=row[0],taskdescr=row[1]) for row in cur.fetchall()]
    return render_template('show_tasks.html',tasks=tasks)



@app.route('/searchTasks',methods=['GET','POST'])
def searchTasks():
    if request.method =='POST':
        if not session.get('logged_in'):
            abort(401)
        userid = session.get('userid')
        taskname = request.form['taskname']
        if not taskname:
            cur = g.db.execute("select taskname,taskdescr from tasks where createby='%s' order by createtime desc"%userid)
            tasks = [dict(taskname=row[0],taskdescr=row[1]) for row in cur.fetchall()]
            return render_template('show_tasks.html',tasks=tasks)
        else:
            cur = g.db.execute("select taskname,taskdescr from tasks where createby='%s' and taskname='%s'  order by createtime desc"%(userid,request.form['taskname']))
            if not cur:
                return redirect('show_tasks.html')
            else:
                tasks = [dict(taskname=row[0],taskdescr=row[1]) for row in cur.fetchall()]
                return render_template('show_tasks.html',tasks=tasks)

       

if __name__=='__main__':
   app.run()	