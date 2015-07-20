## Testing environment

I use pyenv for testing. Assuming the virtualenvs ``compdb-2.7`` and
``compdb-3.4`` exist with the appropriate version of Python, one can enable both
via:
```console
$ pyenv local compdb-3.4 compdb-2.7
```
The ``py27`` and ``py34`` envs in ``tox.ini`` should then work without further
configuration.

