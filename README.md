# Components database

[![Build Status](https://travis-ci.org/rjw57/componentsdb.svg?branch=master)](https://travis-ci.org/rjw57/componentsdb)
[![Coverage Status](https://coveralls.io/repos/rjw57/componentsdb/badge.svg?branch=master&service=github)](https://coveralls.io/github/rjw57/componentsdb?branch=master)

My little database for storing electronics components.

## Testing

The requirements for the testing environment are listed in
``tests/requirements.txt``. You can also see the travis configuration for a
minimal working example. The requirements can be installed via:

```console
$ pip install -r test/requirements.txt
```

In addition, a PostgreSQL database must be available. By default the test suite
uses the "componentsdb_testing" database but you can override this via the
``TEST_DATABASE_URI`` environment variable:

```console
$ TEST_DATABASE_URI=postgres:///other_db tox
```

