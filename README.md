[![Build Status](https://travis-ci.org/agiliq/django-blogango.png?branch=master)](https://travis-ci.org/agiliq/django-blogango)

Checkout the application live in use at [http://agiliq.com/blog](http://agiliq.com/blog)

### To quickly try it locally


    cd django-blogango/example/  
    pip install -r ../requirements.txt  
    python manage.py runserver  

### Requirements

1. django-pingback
2. django-xmlrpc
3. django-taggit


    pip install -r requirements.txt

To integrate into your application:
-----------------------------------

0. Install the requirements
1. Include `blogango, `pingback`, `taggit`, `django.contrib.sitemaps` in installed apps.
2. include blog urls in urls.py
    
    url(r'^blog/', include('blogango.urls')),

3. include `blogango.context_processors.extra_context` in settings.`TEMPLATE_CONTEXT_PROCESSORS`
4. if the comments have to verified through AKISMET, set `AKISMET_API_KEY` else set `AKISMET_COMMENT = False`
5. Enable django admin, if not already enabled.

    python manage.py syncdb

6. create blog at `/admin/blogango/blog/add/`
7. check your blog at `/blog/`

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


