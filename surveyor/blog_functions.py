from flask import g, session

from surveyor.db import get_db

from copy import copy, deepcopy
from pandas import read_sql_query
import itertools


def get_experiment_data(db, simulation_period, user_treatment_level):
    '''need to show the user their treatment level information in the 
    appropriate period'''
    experiment_data = read_sql_query(
        "SELECT * FROM experiment_data;", con=db)
    rec_param_demand_data = experiment_data.loc[
        (experiment_data['Period'] == simulation_period) &
        (experiment_data['ID'] == user_treatment_level)
    ]
    return experiment_data, rec_param_demand_data


def get_fig_url(user_treatment_level, simulation_period):
    return '../../static/recFigs/recFig_' \
        + str(user_treatment_level) + '_' \
        + str(simulation_period) + '.png'


def get_slide_url(slide_number):
    return '../../static/Behavioral_Experiment_Slides/Slide'\
            + str(slide_number) + '.png'


def get_rec_url(slide_number):
    return '../../static/Behavioral_Experiment_Recordings/Slide'\
            + str(slide_number) + '.m4a'


def get_contract_metrics(df, v, p, demand_col, q_col):
    df['sales'] = df.apply(lambda x: min(x[demand_col], x[q_col]), axis=1)

    df['lost_sales'] = df.apply(
        lambda x: max(x[demand_col] - x[q_col], 0), axis=1)

    df['profit'] = df['sales']*p - df[q_col]*v
    
    return df


def get_expected_profit(v, p, q):
    '''Based on uniform distribution from 0 to 100. Should change to meet
    needs of experiment.'''
    return p*sum(x/101 for x in range(q+1)) + p*q*(1 - (q + 1)/101) - v*q 

def validate_input():
    '''Should replace this function code with something that represents the 
    constraints of your problem.'''
    return True


def do_validate_instructions(validate, display_dict, request, q_var, submit_type):
    error_list = []
    if validate: 
        display_dict.update(
            {q_var: request.args.get(q_var)}
        )
    else:
        error_list.append('Invalid order input.')
        
    display_dict.update({submit_type + '_errors': error_list,
                        submit_type + '_n_errors': len(error_list)})

    return error_list


