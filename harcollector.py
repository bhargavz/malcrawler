#!/usr/bin/env python

import argparse
import datetime
import os
import time
import urlparse

from selenium import webdriver

from har2stix import Har2Stix

def load_driver(extensions, mime_types, output_dir, download_dir):
    profile = webdriver.FirefoxProfile()

    for extension in extensions:
        profile.add_extension(extension)

    profile.set_preference('extensions.firebug.allPagesActivation', 'on')
    profile.set_preference('extensions.firebug.defaultPanelName', 'net')
    profile.set_preference('extensions.firebug.net.enableSites', True)
    profile.set_preference('extensions.firebug.console.enableSites', True)
    profile.set_preference('extensions.firebug.script.enableSites', True)
    profile.set_preference('extensions.firebug.onByDefault', True)
    profile.set_preference('extensions.firebug.netexport.alwaysEnableAutoExport', True)
    profile.set_preference('extensions.firebug.netexport.showPreview', False)
    profile.set_preference('extensions.firebug.netexport.defaultLogDir', output_dir)
    profile.set_preference('extensions.firebug.netexport.saveFiles', True)
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', download_dir)

    for mime_type in mime_types:
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', mime_type)

    driver = webdriver.Firefox(profile)
    time.sleep(10)
    return driver

def visit_url(driver, url):
    driver.get(url)
    time.sleep(120)
    driver.quit()

def translate_har(har_dir):
    h2s = Har2Stix(har_dir)
    for root, dirs, files in os.walk(har_dir):
        har_files = files
        break
    for har_file in har_files:
        h2s.run(os.path.join(har_dir, har_file))

description = 'Tool for crawling a list of URLs and generate a HAR file for each one'
parser = argparse.ArgumentParser(description=description)
parser.add_argument('list_file', metavar='LIST', help='File containing the list of URLs to crawl')
args, unknown = parser.parse_known_args()

working_dir = os.path.dirname(os.path.realpath(__file__))

list_file = os.path.join(working_dir, args.list_file)

list_fh = open(list_file, 'r')
urls = list_fh.read().splitlines()

home_dir = os.path.expanduser("~")
conf_dir = os.path.join(home_dir, '.harcollector')
firebug = os.path.join(conf_dir, 'firebug-2.0.12-fx.xpi')
netexport = os.path.join(conf_dir, 'netExport-0.9b7.xpi')

extensions = [firebug, netexport]

mime_types_file = os.path.join(conf_dir, 'mime.types')
mt_fh = open('mime_types_file', 'r')
mime_types = mt_fh.read().splitlines()

for url in urls:
    parsed_url = urlparse.urlparse(url)
    hostname = parsed_url.netloc
    timestamp = datetime.datetime.utcnow().isoformat()
    directory = '{}.{}'.format(timestamp, hostname)
    dir_path = os.path.join(working_dir, directory)
    download_dir = os.path.join(dir_path, 'download')
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        os.makedirs(download_dir)
    driver = load_driver(extensions, mime_types, dir_path, download_dir)
    visit_url(driver, url)
    translate_har(dir_path)
