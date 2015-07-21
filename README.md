## Testing environment

The requirements for the testing environment are listed in
``tests/requirements.txt``. They can be installed via:

```console
$ pip install -r test/requirements.txt
```

In addition, a PostgreSQL database must be available. By default the test suite
uses the "componentsdb_testing" database but you can override this via the
``TEST_DATABASE_URI`` environment variable:

```console
$ TEST_DATABASE_URI=postgres:///other_db tox
```

