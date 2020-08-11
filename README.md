# surveyor

This is a python 3 package. This package was designed with Flask to deliver
surveys for behavioral experiments. Some knowledge of the Flask API is 
assumed. The experiments below are for a Windows OS.

1. Ensure that you have virtualenv installed with `pip list`.
2. If you do not have virtualenv installed. Install it with 
`pip install virtualenv`. Otherwise, go to step 3.
3. create a virtual environment called ``venv'', by 
running `virtualenv venv` on the command line. 
4. Run `config` on the command line. 
5. Run `pip install -r requirements.txt` on the command line.
6. Update or create a new `surveyor/static/experiment_data.csv` file.
7. You should now be able to run `flask init-db` to initialize the database
with experiment data. 
8. After the database has been initialized, you may start the application with
`flask run`.

Tests are designed under the pytest framework, and can be run with `pytest` on 
the command line when pytest has been installed. 

Please contact Bryant Cassidey by e-mail tcassidey@crimson.ua.edu for questions.
