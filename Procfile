web: python3 manage.py compilescss && wait && python3 manage.py migrate && wait && python3 manage.py loaddata initial.json && wait && gunicorn gamemuster.wsgi:application --preload --log-file -
beat: celery -A backend beat -l INFO
worker: celery -A backend worker -l INFO