import os

HTML_ATTRIBUTES = {'width': '100%', 
    'cellspacing': '10', 
    'border': 'true', 
    'rules': 'rows',
    'border-color': 'grey'}

TD_HTML_ATTRIBUTES = {'align': 'center'}

SLIDE_DIR = os.path.join(
        os.path.dirname(__file__), 'static', 'Behavioral_Experiment_Slides')

N_SLIDES = len(os.listdir(SLIDE_DIR))

REC_DIR = os.path.join(
        os.path.dirname(__file__), 'static', 'Behavioral_Experiment_Recordings')

SLIDE_CAPTION_DICT = {
    1: 'Welcome to our experiment, and thank you for being here! \
        This presentation will tell you everything you need to know to succeed \
            in the task before you and let you know what you are in for!'
}

QUESTION_DICT = {
                'Fin1': 'Betting 10% of your annual income at the horse races.',
                'Fin2': 'Investing 10% of your annual inome in a moderate \
                        growth diversified fund.',
                'Fin3': 'Betting 10% of your annual income at a high-stakes \
                        poker game.',
                'Fin4': 'Investing 10% of your annual income in a very \
                        speculative stock.',
                'Fin5': 'Betting 10% of your annual income on the outcome of \
                        a sporting event.',
                'Fin6': 'Investing 10% of your annual income in a new \
                        business venture.'
            }

RISK_PREFERENCE_DICT = {
    'RP1': ['50% chance of either 15.64 points or 4 points', 
            '50% chance of either 8 points or 6 points'],
    'RP2': ['50% chance of either 10.67 points or 4 points', 
            '50% chance of either 8 points or 6 points'],
    'RP3': ['50% chance of either 10.20 points or 4 points', 
            '50% chance of either 8 points or 6 points'],
    'RP4': ['50% chance of either 9.64 points or 4 points', 
            '50% chance of either 8 points or 6 points'],
    'RP5': ['50% chance of either 9.61 points or 4 points', 
            '50% chance of either 8 points or 6 points'],
    'RP6': ['50% chance of either 9.31 points or 4 points', 
            '50% chance of either 8 points or 6 points'],
    'RP7': ['50% chance of either 8.87 points or 4 points', 
            '50% chance of either 8 points or 6 points'],
    'RP8': ['50% chance of either 8.15 points or 4 points', 
            '50% chance of either 8 points or 6 points'],
    'RP9': ['50% chance of either 16 points or 4 points', 
            '50% chance of either 12 points or 8 points'] 
}

UNFORTUNATE_RP9 = {0: ['4', '8'], 1: ['12', '16']}

