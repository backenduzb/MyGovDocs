set -e

python manage.py makemigrations --no-input
python manage.py migrate --no-input

python manage.py collectstatic --no-input

python manage.py makeadmin 

gunicorn config.wsgi:application -w 2 -b 0.0.0.0:8000
