import pytest
from flask import g, session, request
from surveyor.db import get_db
from surveyor.db import get_treatment_levels, get_n_periods


def test_index(client, auth):
    response = client.get('/', follow_redirects=True)
    print(response.data)
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/', follow_redirects=True)
    assert b'Log Out' in response.data


def test_login_required(client):
    response = client.post('/survey')
    assert response.headers['Location'] == 'http://localhost/auth/login'


def test_survey(client, app, auth):
    # with client:
    #     auth.login()
    #     with app.app_context():
    #         db = get_db()

    #         # update the user stage to demographics
    #         db.execute("UPDATE user"
    #                     " SET current_stage = ?, simulation_period = ?"
    #                     " WHERE id = ?",
    #                     ('demographics', 1, session["user_id"]))
    #         db.commit()

    # we need to test for each treatment level
    with app.app_context():
        min_treatment_level, max_treatment_level = get_treatment_levels()
        n_simulation_periods = get_n_periods()
    for treatment_level in range(
        min_treatment_level, 
        max_treatment_level + 1):
        with client:
            auth.login()
            # update the treatment level
            with app.app_context():
                db = get_db()
                db.execute("UPDATE user"
                        " SET current_stage = ?,"
                        " simulation_period = ?, treatment_level = ?"
                        " WHERE id = ?",
                        ('demographics', 
                        1, treatment_level, 
                        session["user_id"]))
                db.commit()
        with client:
            client.post('/survey')
            with app.app_context():
                db = get_db()
                stage = db.execute(
                    "SELECT current_stage FROM user WHERE id = ?", 
                    (session["user_id"],)).fetchone()[0]
                assert stage == 'cognitive'
        with client:
            client.post('/survey')
            with app.app_context():
                db = get_db()
                temp_data = db.execute(
                        "SELECT current_stage, simulation_period"
                        " FROM user WHERE id = ?", 
                        (session["user_id"],)).fetchone()
                assert temp_data[0] == 'simulation'
                assert temp_data[1] == 1

        for period in range(1, n_simulation_periods + 1):
            with client:
                client.post('/survey', data=dict(
                    decision_Q=5))

                with app.app_context():
                    db = get_db()
                    temp_data = db.execute(
                        "SELECT current_stage, simulation_period"
                        " FROM user WHERE id = ?", 
                        (session["user_id"],)).fetchone()
                    if period < n_simulation_periods:
                        assert temp_data[0] == 'simulation'
                        assert temp_data[1] == period + 1
                    else:
                        assert temp_data[0] == 'risk'

        with client:
            answer_dict = {'Fin' + str(x): 5 for x in range(1, 7)}
            answer_dict.update({'RP' + str(x): 0 for x in range(1, 10)})
            client.post('/survey', data=answer_dict)
            with app.app_context():
                db = get_db()
                stage = db.execute(
                    "SELECT current_stage FROM user WHERE id = ?", 
                    (session["user_id"],)).fetchone()[0]
                assert stage == 'risk_answer'

        with client:
            client.post('/survey', data=dict(RP10=5))
            with app.app_context():
                db = get_db()
                stage = db.execute(
                    "SELECT current_stage FROM user WHERE id = ?", 
                    (session["user_id"],)).fetchone()[0]
                assert stage == 'thankyou'

        with client:
            client.post('/survey', data=dict(feedback_input='test_feedback'))
            with app.app_context():
                assert 'user_id' not in session
            

            
                    

        
    

            