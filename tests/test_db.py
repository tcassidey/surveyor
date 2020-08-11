import sqlite3

import pytest
from surveyor.db import get_db, get_treatment_levels


def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)


def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('surveyor.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called


def test_n_periods(app):
    '''Checks to make sure
    all treatment levels have the same number of periods. Should move this
    test to tests package.'''
    with app.app_context():
        db = get_db()
        treatment_levels = get_treatment_levels()
        for treatment_level in enumerate(treatment_levels):
            n_periods = db.execute(
                "SELECT MAX(PERIOD) FROM experiment_data where ID = ?;",
                (treatment_level[1],)
            ).fetchone()[0]
            if treatment_level[0] == 0:
                test = n_periods
            else:
                assert n_periods == test