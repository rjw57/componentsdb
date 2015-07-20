from setuptools import setup, find_packages

setup(
    name="componentsdb",
    version="0.1",
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'future',
        'psycopg2',
        'pyjwt',
        'sqlalchemy',
    ],
)
