# manage.py

import os

from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand

from catalog import app, db
from catalog.models import User


app.config.from_object(os.environ['APP_SETTINGS'])

migrate = Migrate(app, db)
manager = Manager(app)

# migrations
manager.add_command('db', MigrateCommand)


manager.add_command('runserver', Server(host='0.0.0.0', port=5000))

@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()


@manager.command
def drop_db():
    """Drops the db tables."""
    db.drop_all()


@manager.command
def create_user():
    """Creates the admin user."""
    db.session.add(User(
        email="pvignola@carnival.com",
        password="Pierva1234"
        )
    )
    db.session.commit()


if __name__ == '__main__':
    manager.run()
