# https://medium.com/@gevezex/ubuntu-anaconda-env-django-apache-mod-wsgi-howto-in-10-steps-c9008e1d8bfe
import sys
sys.path.insert(0, "/root/kriso-web/season-flask/public")

from app import app as application