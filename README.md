# PyRS990

It's a pun. Get it?

A Python application that can grab all sorts of IRS Form 990 data on non-profit organizations and
put it into a format that can be consumed easily.

## Running

For now you need to clone the repo to use it. Eventually we'll package it.

  1. Make sure you have Python 3.8 available
  1. Install `pipenv` - `pip install --user pipenv`
  1. Clone the whole repo, `cd` into the `pyrs990` directory
  1. Install dependencies - `pipenv sync`
  1. Run it, some examples are below:
      1. `pipenv run python -m pyrs990 --zip 59801 --use-disk-cache`
      1. ...more examples coming soon
  1. Run the commands again, notice the cache speedup
  1. The cache is set to `./.pyrs990-cache/`

## Development

  1. Make sure you have Python 3.8 available
  1. Install `pipenv` - `pip install --user pipenv`
  1. Clone the whole repo, `cd` into the `pyrs990` directory
  1. Install dependencies - `pipenv sync --dev`
  1. Make your changes
  1. If you need to add dependencies:
    1. `pipenv install coolpkg`
    1. `pipenv lock` (updates the lock file)
  1. Make a pull request
