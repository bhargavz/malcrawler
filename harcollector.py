#!/usr/bin/env python

import argparse
import datetime
import os
import time
import urlparse

from selenium import webdriver

def load_driver(output_dir):
    home_dir = os.path.expanduser("~")
    add_on_dir = os.path.join(home_dir, '.harcollector')
    firebug = os.path.join(add_on_dir, 'firebug-2.0.12-fx.xpi')
    netexport = os.path.join(add_on_dir, 'netExport-0.9b7.xpi')

    profile = webdriver.FirefoxProfile()
    profile.add_extension(firebug)
    profile.add_extension(netexport)
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
    profile.set_preference('browser.download.dir', output_dir)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/x-msdownload')

    driver = webdriver.Firefox(profile)
    time.sleep(10)
    return driver

def visit_url(driver, url):
    driver.get(url)
    time.sleep(120)
    driver.quit()

description = 'Tool for crawling a list of URLs and generate a HAR file for each one'
parser = argparse.ArgumentParser(description=description)
parser.add_argument('list_file', metavar='LIST', help='File containing the list of URLs to crawl')
args, unknown = parser.parse_known_args()

working_dir = os.path.dirname(os.path.realpath(__file__))

list_file = os.path.join(working_dir, args.list_file)

list_fh = open(list_file, 'r')
urls = list_fh.read().splitlines()

for url in urls:
    parsed_url = urlparse.urlparse(url)
    hostname = parsed_url.netloc
    timestamp = datetime.datetime.utcnow().isoformat()
    directory = '{}.{}'.format(timestamp, hostname)
    dir_path = os.path.join(working_dir, directory)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    driver = load_driver(dir_path)
    visit_url(driver, url)
