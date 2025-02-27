# Internet Archive Reference Inventory [IARI](https://www.wikidata.org/wiki/Q117023013)
This tool is capable of fetching, extracting, transforming and storing
reference information from Wikipedia articles as [structured data](https://www.wikidata.org/wiki/Q26813700).

IARI is currently an API with a few endpoints which hopefully makes it easy for others
to interact with.

On the longer term we are planning on populating a [Wikibase.cloud](https://wikibase.cloud/) instance
based on the data we extract.
We call this resulting database Wikipedia Citations Database (WCD).

IARI has been developed by [James Hare](https://www.wikidata.org/wiki/Q23041486)
and [Dennis Priskorn](https://www.wikidata.org/wiki/Q111016131) as part of the
[Turn All References Blue project](https://www.wikidata.org/wiki/Q115136754) which is led by
Mark Graham, head of The
[Wayback Machine](https://www.wikidata.org/wiki/Q648266) department of the
[Internet Archive](https://www.wikidata.org/wiki/Q461).

There are [at least 200 million references in at least 40 million articles](
https://ieeexplore.ieee.org/abstract/document/9908858)
and together with the article text in the Wikipedias
one of the most valuable collections of knowledge ever made by humans,
see [size comparison](https://en.wikipedia.org/wiki/Wikipedia:Size_comparisons).

The endpoint providing a detailed analysis of a Wikipedia article and its references
enable wikipedians to get an overview of the state of the references and
build tools that help curate and improve the references.

This is part of a wider initiative help raise the quality of references in
Wikipedia to enable everyone in the world to make decisions
based on trustworthy knowledge
that is derived from trustworthy sources.

# Features
IARI features a number of endpoints that help patrons
get structured data about references in a Wikipedia article:
* an _article_ endpoint which analyzes a given article and returns basic statistics about it
* a _references_ endpoint which gives back all ids of references found
* a _reference_ endpoint which gives back all details about a reference including templates and wikitext
* a _check-url_ endpoint which looks up the URL and gives back
standardized information about its status
* a _check-doi_ endpoint which looks up the DOI and gives back
standardized information about it from [FatCat](https://fatcat.wiki/), OpenAlex and Wikidata
including abstract, retracted status, and more.
* a _pdf_ endpoint which extracts links both from annotations and free text from PDFs.
* a _xhtml_ endpoint which extracts links both from any XHTML-page.

# Limitations
See known limitations under each endpoint below.

# Supported Wikipedias
Currently we support a handful of the 200+ language versions of Wikipedia
but we plan on extending the support to all Wikipedia language versions
and you can help us by submitting sections to search for references in issues and
pull requests.

We also would like to support non-Wikimedia wikis using MediaWiki in the future
and perhaps also any webpage on the internet with outlinks (e.g. news articles).

## Wikipedia templates
English Wikipedia for example has hundreds of special reference templates in use
and a handful of widely used generic templates.
WARI exposes them all when found in a reference.

## Reference types detected by the ArticleAnalyzer
We support detecting the following types. A reference cannot have multiple types.
We distinguish between two main types of references:
1)  **named reference** - type of reference with only a name and no content e.g. '<ref name="INE"/>' (Unsupported
beyond counting because we have not decided if they contain any value)
2) **content reference** - reference with any type of content
   1) **general reference** - subtype of content reference which is outside a <ref></ref> and usually found in
   sections called "Further reading" or "Bibliography"
   (unsupported but we want to support it, see
   https://github.com/internetarchive/wcdimportbot/labels/general%20reference)
    ![image](https://user-images.githubusercontent.com/68460690/208092363-ba4b5346-cad7-495e-8aff-1aa4f2f0161e.png)
   2) **footnote reference** - subtype of content reference which is inside a <ref> (supported partially, see below)

Example of a URL-template reference:
`<ref>Mueller Report, p12 {{url|http://example.com}} {{bare url inline}}</ref>`
This is a content reference -> a footnote reference -> a mixed reference with a URL template.

Example of an plain text reference:
`<ref>Muller Report, p12</ref>`
This is a footnote reference -> content reference -> Short citation reference aka naked named footnote.

# Endpoints
## Checking endpoints
### Check URL
the check-url endpoint accepts the following parameters:
* url (mandatory)
* refresh (optional)
* testing (optional)
* timeout (optional)

On error it returns 400.

#### Known limitations
Sometimes we get back a 403 because an intermediary like Cloudflare detected that we are not a person behind a browser doing the request. We don't have any ways to detect these soft200s.

Also sometimes a server returns status code 200 but the content is an error page or any other content than what the person asking for the information wants. These are called soft404s and we currently do not make any effort to detect them.

You are very welcome to suggest improvements by opening an issue or sending a pull request. :)

## Statistics
### article
the statistics/article endpoint accepts the following parameters:
* url (mandatory)
* refresh (optional)
* testing (optional)

On error it returns 400. On timeout it returns 504 or 502 
(this is a bug and should be reported).

It will return json similar to:
```
{
    "wari_id": "en.wikipedia.org.999263",
    "lang": "en",
    "page_id": 999263,
    "dehydrated_references": [
        {
            "id": "cfa8b438",
            "template_names": [],
            "type": "footnote",
            "footnote_subtype": "named",
            "flds": [],
            "urls": [],
            "titles": [],
            "section": "History"
        },
        {
            "id": "1db10c83",
            "template_names": [
                "citation"
            ],
            "type": "footnote",
            "footnote_subtype": "content",
            "flds": [
                "hydroretro.net"
            ],
            "urls": [
                "http://www.hydroretro.net/etudegh/sncase.pdf"
            ],
            "titles": [
                "Les r\u00e9alisations de la SNCASE"
            ],
            "section": "History"
        }
    ],
    "reference_statistics": {
        "named": 10,
        "footnote": 20,
        "content": 21,
        "general": 1
    },
    "served_from_cache": false,
    "site": "wikipedia.org",
    "timestamp": 1684217693,
    "isodate": "2023-05-16T08:14:53.932785",
    "timing": 0,
    "title": "SNCASO",
    "fld_counts": {
        "aviafrance.com": 3,
        "flightglobal.com": 2,
        "gouvernement.fr": 1,
        "jewishvirtuallibrary.org": 1,
        "hydroretro.net": 1,
        "google.com": 1
    },
    "urls": [
        "http://www.hydroretro.net/etudegh/sncase.pdf",
        "http://www.aviafrance.com/aviafrance1.php?ID_CONSTRUCTEUR=1145&ANNEE=0&ID_MISSION=0&CLE=CONSTRUCTEUR&MOTCLEF=",
        "https://www.gouvernement.fr/partage/9703-vol-historique-du-premier-avion-a-reaction-francais-le-so-6000-triton",
        "https://books.google.com/books?id=3y0DAAAAMBAJ&pg=PA128",
        "http://www.flightglobal.com/pdfarchive/view/1953/1953%20-%201657.html",
        "https://www.flightglobal.com/pdfarchive/view/1959/1959%20-%201053.html",
        "http://xplanes.free.fr/so4000/so4000-5.htm",
        "http://www.jewishvirtuallibrary.org/sud-ouest-s-o-4050-vautour",
        "http://www.aviafrance.com/constructeur.php?ID_CONSTRUCTEUR=1145",
        "http://www.aviafrance.com"
    ],
    "ores_score": {
        "prediction": "GA",
        "probability": {
            "B": 0.3001074961272599,
            "C": 0.2989581851995906,
            "FA": 0.03238239107761332,
            "GA": 0.33793161511968084,
            "Start": 0.0251506380008608,
            "Stub": 0.005469674474994447
        }
    }
}
```
#### Known limitations
* the general references parsing relies on 2 things:
  * a manually supplied list of sections to search using the 'regex' to the article and all endpoints. The list is case insensitive and should be delimited by the '|' character.
  * that every line with a general reference begins with a star character (*)

Any line that doesn't begin with a star is ignored.

### references
the statistics/references endpoint accepts the following parameters:
* wari_id (mandatory, str) (this is obtained from the article endpoint)
* all (optional, boolean) (default: false)
* offset (optional, int) (default: 0)
* chunk_size (optional, int) (default: 10)

On error it returns 400. If data is not found it returns 404.

It will return json similar to:
```
{
    "total": 31,
    "references": [
        {
            "id": "cfa8b438",
            "template_names": [],
            "wikitext": "<ref name = \"Hartmann1\" />",
            "type": "footnote",
            "footnote_subtype": "named",
            "flds": [],
            "urls": [],
            "templates": [],
            "titles": [],
            "section": "History",
            "served_from_cache": true
        },
    ]
}
```
#### Known limitations
None

### reference
the statistics/reference/id endpoint accepts the following parameters:
* id (mandatory) (this is unique for each reference and is obtained from the article or references endpoint)

On error it returns 400. If data is not found it returns 404.

It will return json similar to:
```
{
    "id": "cfa8b438",
    "template_names": [],
    "wikitext": "<ref name = \"Hartmann1\" />",
    "type": "footnote",
    "footnote_subtype": "named",
    "flds": [],
    "urls": [],
    "templates": [],
    "titles": [],
    "section": "History",
    "served_from_cache": true
}
```
#### Known limitations
None

### PDF
the statistics/pdf endpoint accepts the following parameters:
* url (mandatory)
* refresh (optional)
* testing (optional)
* timeout (optional)

On error it returns 400.

The `urls_fixed` object has an array of fixed url fragments in case any were fixed. See [this output](https://archive.org/services/context/wari/v2/statistics/pdf?url=https://s3.documentcloud.org/documents/23782225/mwg-fdr-document-04-16-23-1.pdf&refresh=true).

It will return json similar to:
```
{
    "words_mean": 213,
    "words_max": 842,
    "words_min": 41,
    "annotation_links": [
        {
            "url": "https://web.archive.org/web/20210501230502/cisa.gov/mdm",
            "page": 0
        },
        {
            "url": "https://web.archive.org/web/20210501230502/cisa.gov/mdm",
            "page": 0
        },
        {
            "url": "https://web.archive.org/web/20210501230502/cisa.gov/mdm",
            "page": 0
        },
        {
            "url": "https://web.archive.org/web/20210501230502/cisa.gov/mdm",
            "page": 0
        },
        {
            "url": "https://judiciary.house.gov/media/press-releases/chairman-jim-jordan-subpoenas-big-tech-executives",
            "page": 0
        },
        {
            "url": "https://rumble.com/v1gx8h7-dhss-foreign-to-domestic-disinformation-switcheroo.html",
            "page": 1
        },
        {
            "url": "https://web.archive.org/web/20230224163731/cisa.gov/mdm",
            "page": 3
        },
        {
            "url": "https://www.cisa.gov/topics/election-security/foreign-influence-operations-and-disinformation",
            "page": 3
        },
        {
            "url": "https://report.foundationforfreedomonline.com/8-29-22.html",
            "page": 3
        }
    ],
    "text_links": [
        {
            "url": "https://www.cisa.gov/topics/election-security/foreign-influence-operations-and-disinformationAll",
            "page": 3
        }
    ],
    "text_links_total": 1,
    "annotation_links_total": 9,
    "url": "https://www.foundationforfreedomonline.com/wp-content/uploads/2023/03/FFO-FLASH-REPORT-REV.pdf",
    "timeout": 2,
    "urls_fixed": [],
    "pages_total": 6,
    "timestamp": 1683621700,
    "isodate": "2023-05-09T10:41:40.148210",
    "id": "a07f3f88",
    "refreshed_now": true
}
```

This output permits the data consumer to count number of links per page, which links or domains appear most, etc.

#### Known limitations
The extraction of URLs from unstructured text in any random PDF is a difficult thing to do reliably. This is because PDF is not a structured data format with clear boundaries between different type of information.

We currently use PyMuPDF to extract all the text as it appears on the page, remove all linebreaks and a use a regex to extract anything looking like a URL. This approach results in some links containing information that was part of the text after.

We are currently investigating if using Machine Learning could improve the output.

You are very welcome to suggest improvements by opening an issue or sending a pull request. :)

### XHTML
the statistics/pdf endpoint accepts the following parameters:
* url (mandatory)
* refresh (optional)
* testing (optional)

On error it returns 400.

It will return json similar to:
```
{
    "links": [
        {
            "context": "<a accesskey=\"t\" href=\"http://www.hut.fi/u/hsivonen/test/xhtml-suite/\" title=\"The main page of this test suite\">This is a link to the <acronym title=\"Extensible HyperText Markup Language\">XHTML</acronym> test suite table of contents.</a>",
            "parent": "<p><a accesskey=\"t\" href=\"http://www.hut.fi/u/hsivonen/test/xhtml-suite/\" title=\"The main page of this test suite\">This is a link to the <acronym title=\"Extensible HyperText Markup Language\">XHTML</acronym> test suite table of contents.</a> The link contain inline markup (<code>&lt;acronym&gt;</code>), has a title and an accesskey \u2018t\u2019.</p>",
            "title": "The main page of this test suite",
            "href": "http://www.hut.fi/u/hsivonen/test/xhtml-suite/"
        },
        {
            "context": "<a href=\"base-target\">This is a relative link.</a>",
            "parent": "<p><a href=\"base-target\">This is a relative link.</a> If the link points to http://www.hut.fi/u/hsivonen/test/base-test/base-target, the user agent supports <code>&lt;base/&gt;</code>. if it points to http://www.hut.fi/u/hsivonen/test/xhtml-suite/base-target, the user agent has failed the test.</p>",
            "title": "",
            "href": "base-target"
        }
    ],
    "links_total": 2,
    "timestamp": 1682497512,
    "isodate": "2023-04-26T10:25:12.798840",
    "id": "fc5aa88d",
    "refreshed_now": false
}
```
#### Known limitations
None

# Installation
Clone the git repo:

`$ git clone https://github.com/internetarchive/iari.git && cd iari`

We recommend checking out the latest release before proceeding.

## Requirements
* python pip
* python gunicorn
* python poetry 
 
## Setup
We use pip and poetry to set everything up.

`$ pip install poetry gunicorn && poetry install`

Lastly setup the directories for the json cache files

`$ ./setup_json_directories.sh` 
 
## Run
Run these commands in different shells or in GNU screen.

Start GNU screen (if you want to have a persisting session)

`$ screen -D -RR`

### Development mode
Run it with
`$ ./run-debug-api.sh`

Test it in another Screen window or local terminal with
`$ curl -i "localhost:5000/v2/statistics/article?regex=external%20links&url=https://en.wikipedia.org/wiki/Test"`

### Production mode
Run it with
`$ ./run-api.sh`

Test it in another Screen window or local terminal with
`$ curl -i "localhost:8000/v2/statistics/article?regex=external%20links&url=https://en.wikipedia.org/wiki/Test"`

# Deployed instances
See [KNOWN_DEPLOYED_INSTANCES.md](KNOWN_DEPLOYED_INSTANCES.md)

# Diagrams
## IARI
### Components
![image](diagrams/components.png)

# History of this repo
* version 1.0.0 a proof of concept import tool based on WikidataIntegrator (by James Hare)
* version 2.0.0+ a scalable ETL-framework with an API and capability of reading EventStreams (by Dennis Priskorn)
* version 3.0.0+ WARI, a host of API endpoints that returns statistics
about a Wikipedia article and its references. (by Dennis Priskorn)
* version 4.0.0+ IARI, a host of API endpoints that returns statistics
about both Wikipedia articles and its references and can extract links from any PDF or XHTML page. (by Dennis Priskor

# License
This project is licensed under GPLv3+. Copyright Dennis Priskorn 2022
The diagram PNG files are CC0.

# Further reading and installation/setup
See the [development notes](DEVELOPMENT_NOTES.md)
