from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import session
from werkzeug.exceptions import abort

from surveyor.auth import login_required
from surveyor.db import get_db, get_n_periods

from copy import copy
from pandas import read_sql_query, DataFrame
from numpy import nan
from numpy import round as np_round
import itertools
import os
from datetime import datetime

import surveyor.blog_functions as blog_functions
from surveyor.blog_parameters import HTML_ATTRIBUTES, TD_HTML_ATTRIBUTES, \
    SLIDE_DIR, N_SLIDES, REC_DIR, QUESTION_DICT, RISK_PREFERENCE_DICT, \
    UNFORTUNATE_RP9, SLIDE_CAPTION_DICT

bp = Blueprint("blog", __name__)

shuttle_dict = {'demographics': 'cognitive',
                        'cognitive': 'simulation',
                        'simulation': 'risk',
                        'risk': 'risk_answer',
                        'risk_answer': 'thankyou',
                        'thankyou': 'simulation_complete'}

################################################################################
        ############################################################
        ############---------- HOME PAGE -----------################
        ############################################################
################################################################################
@bp.route("/", methods=("GET", "POST"))
@login_required
def index():
    """Home page. The user will see an overall welcome message, then 
    be able to flip between slides to see instructions for the simulation."""

    db = get_db()
    user_data = db.execute(
        "SELECT * FROM user WHERE id = ?",
        (session["user_id"],)
    ).fetchone()
    user_slide_number = user_data['slide_number']
    fig_url = blog_functions.get_slide_url(user_slide_number)
    slide_recording = blog_functions.get_rec_url(user_slide_number)

    if request.method == 'POST':
        if request.form.get('action') == 'Next Slide':
            if user_slide_number < N_SLIDES:
                db.execute("UPDATE user"
                        " SET slide_number = ?"
                        " WHERE id = ?;",
                        (user_slide_number + 1,
                        session["user_id"]))
                db.commit()
                return redirect(url_for('blog.index'))

        if request.form.get('action') == 'Previous Slide':
            if user_slide_number > 1:
                db.execute("UPDATE user"
                        " SET slide_number = ?"
                        " WHERE id = ?;",
                        (user_slide_number - 1,
                        session["user_id"]))
                db.commit()
                return redirect(url_for('blog.index'))

    return render_template("blog/index.html", 
                            fig_url=fig_url, 
                            slide_caption=SLIDE_CAPTION_DICT[user_slide_number],
                            slide_recording=slide_recording,
                            user_slide_number=user_slide_number)

################################################################################
        ############################################################
        ##########---------- SURVEY PAGES -----------###############
        ############################################################
################################################################################
@bp.route("/survey", methods=("GET", "POST"))
@login_required
def survey():
    """Survey home page."""
    N_SIMULATION_PERIODS = get_n_periods()
    db = get_db()
    user_data = db.execute(
        "SELECT * FROM user WHERE id = ?",
        (session["user_id"],)
    ).fetchone()
    user_stage = user_data['current_stage']
    simulation_period = user_data['simulation_period']
    user_treatment_level = user_data['treatment_level']
    display_dict = {}

    if user_stage == 'simulation':
        fig_url = \
            blog_functions.get_fig_url(user_treatment_level, simulation_period)

        experiment_data, rec_param_demand_data = \
            blog_functions.get_experiment_data(
                db, simulation_period, user_treatment_level)

        rec_param_demand_data_cols = ['Q_rec', 'v', 'p']
        display_dict.update({x: int(rec_param_demand_data[x].tolist()[0])
                                    for x in rec_param_demand_data_cols})
        show_recs = True

        calc_decision_suffixes = ['_Q']
        calc_decision_list = [
            x + y for x in ['calc', 'decision'] for y in calc_decision_suffixes
        ]
        display_dict.update(
            {x: 0 for x in calc_decision_list})
        display_dict.update(
            {'calc_errors': [],
            'calc_n_errors': 0,
            'decision_errors': [],
            'decision_n_errors': 0,
            'expected_profit': 0}
        )

        # need an empty dataframe before history is made
        temp_display_df_cols = ['Period',  
                    'Ordered From Supplier', 
                    'Demand',
                    'Profit ($)']

        if ((simulation_period >= 2) 
            & (simulation_period <= N_SIMULATION_PERIODS)):
            # get the relevant historical data and display it as a table
            temp_exp_df = experiment_data.loc[
                (experiment_data['ID'] == user_treatment_level)
                & (experiment_data['Period'] < simulation_period)][
                ['Period', 'Demand']]

            # now get the ful contracts table for this user
            temp_user_contracts_df = read_sql_query(
                "SELECT * FROM contracts WHERE user_id = "\
                + str(session["user_id"]), con=db
            )

            temp_display_df = temp_exp_df.merge(
                temp_user_contracts_df, 
                how='left', 
                left_on='Period', right_on='simulation_period')

            temp_display_df = blog_functions.get_contract_metrics(
                temp_display_df, 
                display_dict['v'], 
                display_dict['p'], 
                'Demand', 
                'q' 
            ) 

            temp_display_df.rename(
                {'q': 'Ordered From Supplier',
                'sales': 'Sales (Units)',
                'lost_sales': 'Lost Sales (Units)',
                'profit': 'Profit ($)'}, axis=1, inplace=True)
                
            cols = ['Period', 'Demand', 
                    'Ordered From Supplier', 
                    'Profit ($)']

            temp_display_df = temp_display_df[temp_display_df_cols]
        else:
            temp_display_df = DataFrame(columns=temp_display_df_cols)

    if request.method == 'GET':
        if user_stage == 'simulation':
            if request.args.get('action') == 'Calculate': 
                validate = blog_functions.validate_input()
                error_list = blog_functions.do_validate_instructions(
                    validate, display_dict, request, 'calc_Q', 'calc'
                )
                    
                if len(error_list) == 0:
                    expected_profit = blog_functions.get_expected_profit(
                        int(display_dict['v']), 
                        int(display_dict['p']),
                        int(request.args.get('calc_Q'))
                    ) 

                    display_dict.update({
                        'expected_profit': np_round(expected_profit, 2)
                        })

                    update_calculator_count = user_data['calculator_count'] + 1

                    db.execute("UPDATE user"
                        " SET calculator_count = ?"
                        " WHERE id = ?;",
                        (update_calculator_count,
                        session["user_id"]))
                    db.commit()
                
                return render_template("blog/" + user_stage + ".html",
                    display_dict=display_dict,
                    simulation_period=simulation_period,
                    historical_table=temp_display_df.to_html(
                        index=False, 
                        justify='left'),
                    fig_url=fig_url,
                    show_recs=show_recs)
            
            if simulation_period <= N_SIMULATION_PERIODS:
                return render_template("blog/" + user_stage + ".html",
                    display_dict=display_dict,
                    simulation_period=simulation_period,
                    historical_table=temp_display_df.to_html(
                        index=False, 
                        justify='left'),
                    fig_url=fig_url,
                    show_recs=show_recs)
            
            else:
                db.execute("UPDATE user"
                        " SET current_stage = ?"
                        " WHERE id = ?;",
                        (shuttle_dict[user_stage], session["user_id"]))
                db.commit()
        
        if user_stage == 'risk':
            return render_template("blog/" + user_stage + ".html",
                    question_dict=QUESTION_DICT,
                    risk_preference_dict=RISK_PREFERENCE_DICT)

        if user_stage == 'risk_answer':
            given_answer = RISK_PREFERENCE_DICT['RP9'][user_data['RP9']]
            answer_list = ['You chose ' + given_answer + '.']
            answer_list.extend(
                ['The computer chose ' + UNFORTUNATE_RP9[user_data['RP9']][0] \
                    + ' points.'])
            answer_list.extend(['If you would have chosen "' + \
            RISK_PREFERENCE_DICT['RP9'][1 - user_data['RP9']] + 
            '", you would have won ' + \
            UNFORTUNATE_RP9[user_data['RP9']][1] + ' points!'])
            return render_template("blog/" + user_stage + ".html",
                answer_list=answer_list)

        return render_template("blog/" + user_stage + ".html")
    
    if request.method == 'POST':
        if user_stage == 'demographics':
            gender = request.form.get('gender')
            age = request.form.get('age')
            sc = request.form.get('sc')
            procurement = request.form.get('procurement')

            db.execute("UPDATE user"
                        " SET gender = ?, age = ?, sc_exp = ?,"
                        " procurement_exp = ?, current_stage = ?"
                        " WHERE id = ?;",
                        (gender, age, sc, procurement, 
                        shuttle_dict[user_stage], session["user_id"]))
            db.commit()

        if user_stage == 'cognitive':
            db.execute("UPDATE user"
                        " SET CRT1 = ?, CRT2 = ?, CRT3 = ?,"
                        " CRT4 = ?, CRT5 = ?, CRT6 = ?, CRT7 = ?,"
                        " current_stage = ?, enter_simulation = ?"
                        " WHERE id = ?;",
                        (request.form.get("CRT1"), 
                        request.form.get("CRT2"),
                        request.form.get("CRT3"),
                        request.form.get("CRT4"),
                        request.form.get("CRT5"),
                        request.form.get("CRT6"),
                        request.form.get("CRT7"), 
                        shuttle_dict[user_stage], 
                        datetime.now(),
                        session["user_id"]))
            db.commit()

        if user_stage == 'simulation':
            if simulation_period <= N_SIMULATION_PERIODS:
                validate = blog_functions.validate_input()
                error_list = blog_functions.do_validate_instructions(
                    validate, display_dict, request, 'decision_Q', 'decision'
                )

                if len(error_list) == 0:
                    db.execute("INSERT INTO contracts"
                        "(user_id, simulation_period, q, time_stamp,"
                        " calculator_count)"
                        "VALUES (?, ?, ?, ?, ?);",
                        (session["user_id"], 
                        simulation_period, 
                        int(request.form.get('decision_Q')),
                        datetime.now(), 
                        user_data['calculator_count'])
                    )
                    db.commit()

                    update_simulation_period = simulation_period + 1

                    if simulation_period < N_SIMULATION_PERIODS:
                        db.execute("UPDATE user"
                                " SET simulation_period = ?"
                                " WHERE id = ?",
                                (update_simulation_period,
                                session["user_id"]))
                        db.commit()
                    else:
                        # go to the risk survey
                        db.execute("UPDATE user"
                                " SET current_stage = ?"
                                " WHERE id = ?;",
                                (shuttle_dict[user_stage], session["user_id"]))
                        db.commit()
                else:
                    return render_template("blog/" + user_stage + ".html",
                                    display_dict=display_dict,
                                    simulation_period=simulation_period,
                                    historical_table=temp_display_df.to_html(
                                                    index=False, 
                                                    justify='left'),
                                    fig_url=fig_url,
                                    show_recs=show_recs)
        
        if user_stage == 'risk':
            fin_answer_dict = {x: request.form.get(x) 
                for x in QUESTION_DICT.keys()
            }
            risk_answer_dict = {x: request.form.get(x) 
                for x in RISK_PREFERENCE_DICT.keys()
            }
            
            all_updates = [shuttle_dict[user_stage]]
            all_updates.extend([int(fin_answer_dict[x]) 
                for x in fin_answer_dict.keys()])
            all_updates.extend([int(risk_answer_dict[x]) 
                for x in risk_answer_dict.keys()])
            all_updates.extend([session["user_id"]])
            
            db.execute("UPDATE user"
                    " SET current_stage = ?,"
                    " Fin1 = ?, Fin2 = ?, Fin3 = ?, Fin4 = ?, Fin5 = ?, Fin6 = ?,"
                    " RP1 = ?, RP2 = ?, RP3 = ?, RP4 = ?, RP5 = ?, RP6 = ?,"
                    " RP7 = ?, RP8 = ?, RP9 = ?"
                    "WHERE id = ?;",
                    tuple(all_updates)
                    )
            db.commit()

        if user_stage == 'risk_answer':
            answer = request.form.get('RP10')
            db.execute("UPDATE user"
                    " SET current_stage = ?,"
                    " RP10 = ?"
                    "WHERE id = ?;",
                    (shuttle_dict[user_stage], answer, session["user_id"])
                    )
            db.commit()

        if user_stage == 'thankyou':
            feedback = request.form.get('feedback_input')
            db.execute("UPDATE user"
                        " SET feedback = ?, current_stage = ?"
                        " WHERE id = ?;",
                        (feedback, shuttle_dict[user_stage], 
                        session["user_id"]))
            db.commit()
            session.clear()
            return redirect(url_for("blog.survey"))
                
        return redirect(url_for("blog.survey"))
    

    
    

    

