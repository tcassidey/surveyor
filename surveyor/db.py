import sqlite3

import click
from flask import current_app
from flask import g
from flask.cli import with_appcontext

from pandas import read_csv, read_excel
from numpy import int64
import sys
import os


def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()


def get_data(cursor):
    ''' function to get data and column names from a db table'''
    col_names = [x[0] for x in cursor.description]
    data = cursor.fetchall()
    return col_names, data


def get_treatment_levels():
    ''' Returns the minimum, maximum treatment levels from 
    experiment_data.csv'''
    db = get_db()
    treatment_levels = db.execute(
        "SELECT MIN(ID), MAX(ID) FROM experiment_data;").fetchone()
    return treatment_levels[0], treatment_levels[1]


def get_n_periods():
    '''Returns the max number of periods in experiment data. Checks to make sure
    all treatment levels have the same number of periods. Should move this
    test to tests package.'''
    db = get_db()
    n_periods = db.execute(
        "SELECT MAX(PERIOD) FROM experiment_data;"
    ).fetchone()[0]
    return n_periods
            




def init_db():
    """Clear existing data and create new tables."""
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))

    sqlite3.register_adapter(int64, lambda val: int(val))

    CURRENT_PATH = os.path.realpath(__file__)
    APP_PATH = os.path.dirname(CURRENT_PATH)
    EXPERIMENT_DATA = \
        os.path.join(APP_PATH, os.path.join("static", "experiment_data.csv"))
    if os.path.exists(EXPERIMENT_DATA):
        experiment_data = read_csv(EXPERIMENT_DATA)
        experiment_data.to_sql('experiment_data', con=db)

    else:
        raise("No experiment data!")


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


    
