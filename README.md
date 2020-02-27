![PyRS990 Header](pyrs990_header.png)

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

For now you need to clone the repo to use it. Eventually we'll package it.

  1. Make sure you have Python 3.8 available
  1. Install `pipenv` - `pip install --user pipenv`
  1. Clone the whole repo, `cd` into the `pyrs990` directory
  1. Install dependencies - `pipenv sync`
  1. Run it, some very simple examples are below:
      1. `pipenv run python -m pyrs990 --zip 59801 --use-disk-cache`
      1. ...more examples coming soon
  1. Run the commands again, notice the cache speedup
  1. The cache is set to `./.pyrs990-cache/`

### Developer

  1. Make sure you have Python 3.8 available
  1. Install `pipenv` - `pip install --user pipenv`
  1. Clone the whole repo, `cd` into the `pyrs990` directory
  1. Install dependencies - `pipenv sync --dev`
  1. Make your changes
  1. If you need to add dependencies:
      1. `pipenv install coolpkg`
      1. `pipenv lock` (updates the lock file)
  1. Make a pull request

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
