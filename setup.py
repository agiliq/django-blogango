import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

setup(
    name="blogango",
    version="0.1",
    packages=['blogango'],
    package_data={ 'blogango': [ 'templates/*.html',
                                 'templates/blogango/*.html',
                                 ],
                   },
    zip_safe=False,
    author="Agiliq Solutions",
    author_email="hello@agiliq.com",
    description="Blog with django",
    url="http://agiliq.com/",
)
