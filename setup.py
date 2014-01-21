from distutils.core import setup

setup(
    name="django-blogango",
    version="0.6.2",
    packages=['blogango',
              'blogango/conf',
              'blogango/management',
              'blogango/management/commands',
              'blogango/templatetags'
              ],
    package_dir={'blogango': 'blogango'},
    package_data={'blogango': ['templates/*.html',
                               'templates/blogango/*.html',
                               'templates/blogango/admin/*.html',
                               'templates/blogango/admin/*.js',
                               'static/blogango/admin/*.css',
                               'static/blogango/admin/img/*.png',
                               'static/blogango/css/*.css',
                               'static/blogango/images/*.png',
                               'static/blogango/images/*.jpg',
                               'static/blogango/images/*.gif',
                               'static/blogango/js/*.js',
                               ]
    },
    author="Agiliq Solutions",
    author_email="hello@agiliq.com",
    description="A django based blog",
    long_description=
    """
        Blogango is a simple but robust blogging application written with django

        Some of the features include comments using contrib.comments framework,
        backtype and pingback support, rich text using django-markupfield,
        month based archiving, tagging using django-taggit and categorization
    """,
    classifiers = ['Development Status :: 5 - Production/Stable',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                   'Topic :: Internet :: WWW/HTTP :: WSGI',
                   'Topic :: Software Development :: Libraries :: Application Frameworks',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   ],
    url="http://www.agiliq.com/",
    license="Dual Licenced under GPL and BSD",
    platforms=["all"],
)
