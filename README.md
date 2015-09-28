# malcrawler
This tools crawls a list of potentially malicious URLs and extracts indicators from the resulting HAR files.

Before running the tool, create a .harcollector directory in your home directory. You will then need to put the
Firebug and netExport .xpi files in that directory. In addition, please move the mime.types file from the repository
to that directory.

Firebug can be downloaded here:
https://addons.mozilla.org/en-US/firefox/addon/firebug/

netExport can be downloaded here:
http://getfirebug.com/releases/netexport/

usage: harcollector.py [-h] LIST

Tool for crawling a list of URLs and generate a HAR file for each one

positional arguments:
  LIST        File containing the list of URLs to crawl

usage: har2stix.py [-h] HAR

Tool for parsing HAR file and generating MAEC and STIX IOC output

positional arguments:
  HAR         Target HAR file
