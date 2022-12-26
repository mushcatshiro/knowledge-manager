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

## KIVs

- adopting ANKI into the km system
  - subsystem to help generating questions based on each document's gist
  - hints for shortcut-esque questions (i.e. vim short cut for visual mode - v)
  - filter out questions to be answered found within the documents for
    - question list api
    - ANKI challenge
  - when backlog is greater than N cards, batch them evenly in a reasonable duration
- attachble task to documents and to another task
- knowledge graph viz
- md to 80 width wide document for search result's read only mode

## Acknowledgements

- bookmarklet is a fork of/heavily inspired by [this project](https://gist.github.com/codemicro/f7d4d4b687c3ec2e7186ef7efecfcc35) and [the following post](https://www.tdpain.net/blog/a-year-of-reading)
