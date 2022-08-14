import click
from flask_migrate import Migrate
import os
from app import create_app, db
from app.models import Consumer, Destiny, Product, Theme


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Consumer=Consumer, Destiny=Destiny, Product=Product)

@app.cli.command()
# @click.argument('test_names', nargs=-1)
def test():
    """""Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)