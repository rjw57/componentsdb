"""
CLI management script. (Requires flask-script.)

"""
from flask.ext.script import Manager

from componentsdb.app import create_app, db

app = create_app()
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///comp_testing'
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)

manager = Manager(app)

if __name__ == "__main__":
    manager.run()

