import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

setup(
    name="django-blogango",
    version="0.1",
    py_modules=['ez_setup'],
    packages=['blogango',
              'blogango/conf',
              'blogango/management',
              'blogango/management/commands',
              'blogango/templatetags'
              ],
    package_dir={'blogango': 'blogango'},
    package_data={'blogango': ['templates/*.html',
                               'templates/blogango/*.html'
                               ]
    },
    zip_safe=False,
    author="Agiliq Solutions",
    author_email="hello@agiliq.com",
    description="A django based blog",
    long_description=
    """
        Blogango is a simple but robust blogging application written with django
        
        Some of the features include comments using contrib.comments framework,
        backtype and pingback support, rich text using django-markupfield,
        month based archiving, tagging using django-tagging and categorization
    """,
    classifiers = ['Development Status :: 4 - Beta',
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
