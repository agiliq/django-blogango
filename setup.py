import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

setup(
    name="blogango",
    version="0.1",
    packages=['blogango'],
    zip_safe=False,
    author="Agiliq Solutions",
    author_email="hello@agiliq.com",
    description="Blog with django",
    long_description=
    """
        Blogango is a simple but robust blogging application written with django
        
        Some of the features include comments using contrib.comments framework,
        backtype and pingback support, rich text using django-markupfield,
        month based archiving, tagging using django-tagging and categorization
    """,
    url="http://agiliq.com/",
    license="Dual Licenced under GPL and BSD",
    platform="all",
)
