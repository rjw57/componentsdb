from setuptools import setup, find_packages

setup(
    name="componentsdb",
    version="0.1",
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'enum34',
        'flask',
        'flask-sqlalchemy',
        'oauth2client',
        'psycopg2',
        'pyjwt',
        'pyopenssl',
        'sqlalchemy',
    ],
)
