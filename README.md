# Knowledge Manager

project name is inherited from earlier versions which branched out into slightly different/wider scope.

## Setup

### Bookmarklet

1. edit bookmarklet.js accordingly
2. copy bookmarklet.js content to chrome - bookmark manager - add new bookmark - url

```bash
pip install -r requirements.txt
cd bookmarklet
export FLASK_APP=bookmarklet.py
flask init
python bookmarklet.py
```

### web

> do refer to config.py to setup .env prior to running the following commands

push local changes
```bash
python cli --opt push
```

starting web application
```bash
cd web
export FLASK_APP=app.py
flask --app "app:create_app('default')" run
```

test
```bash
cd web
# to print `print()` statement and run specific tests
ENVFILE=.env.test pytest --capture=no test\test_crud\test_crud.py
# to run test in quiet mode
ENVFILE=.env.test pytest -q test\test_crud\test_crud.py
# to run all test
ENVFILE=.env.test pytest
# show coverage
ENVFILE=.env.test pytest --cov=blog/app/ --cov-report html test/test_app/test_view.py
```

> `ENVFILE=.env.test` is needed until hack is fixed

## Acknowledgements

- bookmarklet is a fork of/heavily inspired by [this project](https://gist.github.com/codemicro/f7d4d4b687c3ec2e7186ef7efecfcc35) and [the following post](https://www.tdpain.net/blog/a-year-of-reading)
