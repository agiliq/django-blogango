[![Build Status](https://travis-ci.org/agiliq/django-blogango.png?branch=master)](https://travis-ci.org/agiliq/django-blogango)

[![Coverage Status](https://coveralls.io/repos/agiliq/django-blogango/badge.png?branch=master)](https://coveralls.io/r/agiliq/django-blogango?branch=master)

Checkout the application live in use at [http://agiliq.com/blog](http://agiliq.com/blog)

### To quickly try it locally


    cd django-blogango/example/  
    pip install -r ../requirements.txt  
    python manage.py syncdb --migrate
    python manage.py runserver

Create a Blog instance at `/admin/blogango/blog/add/`. The Blog instance is required for storing blog wide settings, like, number of entries to show per page, title for the blog, tag line for the blog etc.

With Blog instance created, you will be able to access `/blog/`. At this point, no blog entries exist. Create a blog entry at `/admin/blogango/blogentry/add/`.

With a blog entry created, you would be able to see the entry at `/blog/`.

To integrate into your application:
-----------------------------------

0. Install the requirements.
1. Include `blogango`, `pingback`, `taggit`, `django.contrib.sitemaps`, `django_xmlrpc` and `google_analytics` in settings.`INSTALLED_APPS`.
2. Include blog urls in urls.py

    url(r'^blog/', include('blogango.urls')),

3. If the comments have to verified through AKISMET, set settings.`AKISMET_API_KEY`.
4. Enable django admin, if not already enabled.

    python manage.py syncdb

5. Create blog at `/admin/blogango/blog/add/`.
6. Check your blog at `/blog/`.

To see it in action.
---------------------------

http://agiliq.com/blog/

Features
-------------------------

* Comment
* Comment moderation
* Category
* Tagging
* RSS
* Akismet Spam Filtering
* Trackback
* Date based archives
* Multi Author
* Supports various markup types
