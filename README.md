![PyRS990 Header](https://github.com/code-for-montana/pyrs990/raw/master/pyrs990_header.png)

![analyze](https://github.com/code-for-montana/pyrs990/workflows/analyze/badge.svg)
![format check](https://github.com/code-for-montana/pyrs990/workflows/format%20check/badge.svg)
![check](https://github.com/code-for-montana/pyrs990/workflows/check/badge.svg)

It's a pun. Get it?

A Python application and library that can grab all sorts of IRS Form 990
data on non-profit organizations and put it into a format that can be
consumed easily by other applications.

## Up and Running

The instructions below should allow you to get the software working
for your purpose (user or developer). If you run into trouble please,
please let us know so that we can update the instructions (or fix the
bug you ran into).

### User

#### Pip Install

**Requires Python 3.8 or greater**

You can install PyRS990 easily using `pip`: `pip install pyrs990` or
`pip install --user pyrs990` if you're not in a virtual environment and
don't want a global install.

#### Docker

Grab one of our docker images from here: <https://hub.docker.com/orgs/codeformontana>
and run it sort of like this:

```shell script
docker run --mount src="${PWD}/data",target=/data,type=bind codeformontana/pyrs990:latest --help
```

Instead of `--help` at the end, add your own command line arguments to
make it do whatever it is you want it to do. You can assume that `/data`
is where any output should be stored for commands that require a path,
files written there will then show up in your current directory outside
the Docker container.

#### Clone the Code

**Requires Python 3.8 or greater**

You can also clone the repo to use it, but this probably isn't the way
to go for non-developers.

  1. Make sure you have Python 3.8 available
  1. Install [Poetry](https://python-poetry.org/) if you don't already have it
  1. Clone the whole repo, `cd` into the `pyrs990` directory
  1. Install dependencies - `poetry install`
  1. Run it, some very simple examples are below:
      1. `poetry run python -m pyrs990 --zip 59801 --use-disk-cache`
      1. ...more examples coming soon
  1. Run the commands again, notice the cache speedup
  1. The cache is set to `./.pyrs990-cache/`

### Developer

This project uses [Poetry](https://python-poetry.org/) because it's pretty slick
and does a lot of stuff automatically and the developers are not usually Python
people, so that's great!

  1. Make sure you have Python 3.8 available
  1. Install [Poetry](https://python-poetry.org/) if you don't already have it
  1. Clone the whole repo, `cd` into the `pyrs990` directory
  1. Install dependencies - `poetry install`
  1. If you need to add dependencies:
      1. `poetry add coolpkg`
  1. Make a pull request!

## Development

### Docker

We ship Docker containers that are pre-configured to run the application. To build
new container images use `make docker-build`. To push them to Docker Hub, use
`make docker-push`. Be sure to do any necessary version updates (see below) before
rebuilding the container images as they will be tagged using the latest version
number.

### Release Process

```shell script
# Assuming you've got the latest master and a clean working directory!
# Bump the version
make version-patch # or "major" or "minor"
git commit -a 'Bump version for release'
git push
# Maybe wait for CI to pass, or do it manually below
make analyze check-format check
# Now we make all the things public
make build publish
make docker-build docker-push
```

### Versioning

Increment the version using `make version-{major, minor, patch}` or update
it manually in the `pyproject.toml` file. This is the source of truth, everything
else will update automatically based on it. If you modify the version manually,
be sure to run `make store-version` to update the code.

Since PyRS990 is both an application and a library, we try to stick to semantic
version rules. Increment the major for breaking changes, the minor for new features,
and the patch for bug fixes and other "behind the scenes" changes.

## About the Data

Right now we pull data that originated with the IRS (hence the silly name)
but we get it from a couple sources and information about what is actually
available is a little spread out as well.

### Structure

There are two indices used to narrow down the list of filing documents
that must be downloaded a satisfy a given query. The first is an
annual index (we refer to it as "Annual" or "Annual Index" in the
code). This index contains all filings processed by the IRS for a
given calendar year.

Note that this does not necessarily have anything
to do with the filing year. An organization might, for example, file
its 2016 990 in either 2017 or 2018 (or even later). There is a field,
described below, called `tax_period` that reflects the filing period.
In the future, we intend to further abstract this so that it is
easier to use.

The annual index also contains a field called `object_id` that tells
us where to find the XML document that corresponds to that row in
the index. PyRS990 abstracts this away, but it is still good to be
aware of it.

The second index is the "Exempt Organizations Business Master File"
distributed by the IRS. We refer to it as the "BMF Index". This
index provides the physical address of each organization, along
with some other helpful information. This allows the data to be
queried by state, zip code, and so on, which greatly reduces the
number of filing documents that must be downloaded for many queries.

Indices may be used to query filing documents from the command
line using various options. Note that there are options for both
indices and for the filing documents themselves. If possible, it
is a good idea to try to use as many index fields as you can to
reduce the number of files you have to download.

See the example queries for more information.

### Sources

The [IRS BMF index files](https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf)
are hosted by the IRS directly and are available by state and region.

[Descriptions of the variables](https://www.irs.gov/pub/irs-soi/eo_info.pdf)
contained in the files and the process used to build them are
also available (it is also linked from the page above).

The annual index files come from an
[AWS S3 bucket](https://registry.opendata.aws/irs990/)
managed by the IRS. The contents of the bucket are described there.

There is also [a readme](https://docs.opendata.aws/irs-990/readme.html)
that demonstrates how to download the files here (it is also linked
from the page above):

The filing documents themselves also come from this same
[AWS S3 bucket](https://registry.opendata.aws/irs990/)
in XML format. For the extremely XML-savvy, you can checked out the
[schema documentation](https://www.irs.gov/e-file-providers/current-valid-xml-schemas-and-business-rules-for-exempt-organizations-modernized-e-file)
on the IRS website. PyRS990 abstracts this away, however,
so there's no real need to understand it if you only want to access the
data in a convenient format.

Finally, while not strictly a data source, the
[IRSx documentation](http://www.irsx.info/) created
by ProPublica contains descriptions of many of the filing fields in a
simple, readable format. For developers, PyRS990 has been designed to
work with the exact XPath selectors listed in the IRSx documentation, so
if you want to add a field to the `Filing` object, this is the place to
look first.
