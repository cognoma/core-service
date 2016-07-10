# Repository for django-cognoma

This repository, under the umbrella of Project Cognoma
(https://github.com/cognoma), holds the source code, under open source
licence, of a runnable django site, a component in the overall system
specified in Project Cognoma. The django site will fulfill the system
requirements specified in the purple box in the middle of the system flow chart
and will contain the following:

* an html interface starting at a home page for anonymous users to visit
  and try out machine learning algorithms, as well as admin pages for
  site admins to be able to manipulate site content

* a Rest API for other components of the system to use to read and write data
  found on the django site.

* a task handler, implemented using celery, to allow users to start long-running
  tasks without being blocked while waiting for them to finish

The site is currently only ready to be run on a developer's machine.  As it
becomes ready for staging, there will need to be instructions added for the
various cloud instances running.  For now, as a developer, one can get it
running on their machine with the following instructions in a command
window:

    > git clone git@github.com:cognoma/django-cognoma.git
    > cd django-cognoma
    > virtualenv env
    > source env/bin/activate
    > pip install -r requirements.txt
    > python manage.py migrate
    > python manage.py createsuperuser
    > python manage.py runserver

Visiting localhost:8000 in a browser should return the home page, currently
the 'It worked' page that comes with a brand new django site.