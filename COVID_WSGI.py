import sys

# add your project directory to the sys.path
project_home = u'\Desktop\Python\COVID'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# need to pass the flask app as "application" for WSGI to work
# for a dash app, that is at app.server
# see https://plot.ly/dash/deployment
from COVID_Website import app

application = app.server
