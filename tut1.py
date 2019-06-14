
"""
pip install flask-sqlalchemy
pip install flask-migrate
pip install flask-mail

cd D:\flask\env
Scripts\activate

cd ..\app
python tut1.py db init
(env) D:\flask\app>python tut1.py db init
D:\flask\env\lib\site-packages\flask_sqlalchemy\__init__.py:835: FSADeprecationWarning: SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and will be disabled by default in the futu
re.  Set it to True or False to suppress this warning.
  'SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and '
Creating directory D:\flask\app\migrations ... done
Creating directory D:\flask\app\migrations\versions ... done
Generating D:\flask\app\migrations\alembic.ini ... done
Generating D:\flask\app\migrations\env.py ... done
Generating D:\flask\app\migrations\README ... done
Generating D:\flask\app\migrations\script.py.mako ... done
Please edit configuration/connection/logging settings in 'D:\\flask\\app\\migrations\\alembic.ini' before proceeding.

python tut1.py db migrate -m "initial migration"
D:\flask\env\lib\site-packages\flask_sqlalchemy\__init__.py:835: FSADeprecationWarning: SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and will be disabled by default in the futu
re.  Set it to True or False to suppress this warning.
  'SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and '
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.env] No changes in schema detected.

python tut1.py db upgrade  # actually calls db.create_all() command
D:\flask\env\lib\site-packages\flask_sqlalchemy\__init__.py:835: FSADeprecationWarning: SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and will be disabled by default in the futu
re.  Set it to True or False to suppress this warning.
  'SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and '
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.


python tut1.py shell
from tut1 import db
db.create_all()

from tut1 import Role, User
admin_role = Role(name="admin")
mod_role = Role(name='Moderator')
user_role = Role(name='User')

user_john = User(username='john', role=admin_role)
user_susan = User(username='susan', role=user_role)
user_david = User(username='david', role=user_role)

db.session.add(admin_role)
db.session.add(mod_role)
db.session.add(user_john)
db.session.add(user_susan)
db.session.add(user_david)
db.session.commit()

admin_role.name="Administrator"
db.session.add(admin_role)
db.session.commit()

Role.query.all()
[<Role 'Administrator'>, <Role 'Moderator'>, <Role 'User'>]
User.query.all()
[<User 'john'>, <User 'susan'>, <User 'david'>]

"""
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_script import Manager
from forms import LoginForm

app = Flask(__name__)
app.config.from_object('config.Config')

manager = Manager(app)
bootstrap = Bootstrap(app)

#DB
from flask_sqlalchemy import SQLAlchemy
import os

# DB - DATABASE CONFIG
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
#app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

#DBMIGRATION
from flask_migrate import Migrate, MigrateCommand
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

#SHELL
from flask_script import Shell







class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

####

# Configuring classes in Shell

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

manager.add_command("shell", Shell(make_context=make_shell_context))
#

@app.route("/login", methods=['GET', 'POST'])
def index():
    name = None
    form = LoginForm()
    if form.validate_on_submit():
        #name = form.username.data
        #form.username.data = ''
        session['username'] = form.username.data
        return redirect(url_for('index'))
    return render_template("tut1/home.html", name=session.get('username'), form=form )

@app.route("/loging", methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        old_session_name = session.get('username')
        if old_session_name != None  and old_session_name != form.username.data:
            flash("Name is changed wrt to session name: session name=" + old_session_name)
        session['username'] = form.username.data
        form.username.data = ''
        return redirect(url_for('login'))
    return render_template("tut1/home.html", name=session.get('username'), form=form)

@app.route("/dbloging",methods=['GET','POST'])
def dblogin():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            user = User(username=form.username.data)
            db.session.add(user)
            session['known'] = False
        else:
            session['known'] = True
        session['username'] = form.username.data
        form.username.data = ''
        return redirect(url_for('dblogin'))
    return render_template('tut1/home.html', name=session.get('username'), form=form, known=session.get('known'))

@app.route("/")
def main():
    return render_template("tut1/mainpage.html")

if __name__ == '__main__':
    manager.run()