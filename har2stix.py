#!/usr/bin/env python

import argparse
import json
import os
import re

from maec.package import Package
from maec.package import MalwareSubject
from stix.core import STIXPackage, STIXHeader
from stix.common.information_source import InformationSource
from stix.indicator.indicator import Indicator
from cybox.core import Object
from cybox.objects.uri_object import URI
from cybox.objects.hostname_object import Hostname
from cybox.objects.address_object import Address

def create_maec(url_indicator):
    package = Package()
    ms = MalwareSubject()
    ms.malware_instance_object_attributes = Object()
    ms.malware_instance_object_attributes.properties = URI(type_=URI.TYPE_URL)
    ms.malware_instance_object_attributes.properties.value = url_indicator
    package.add_malware_subject(ms)
    return package

def init_stix():
    stix_package = STIXPackage()
    stix_header = STIXHeader()
    info_source = InformationSource()
    info_source.description = 'HAR file analysis of visit to malicious URL'
    stix_header.information_source = info_source
    stix_package.stix_header = stix_header
    return stix_package

def create_url_indicator(url_indicator):
    indicator = Indicator()
    indicator.title = 'URL of site hosting malware'
    indicator.add_indicator_type('URL Watchlist')

    url = URI()
    url.value = url_indicator
    url.type_ =  URI.TYPE_URL
    url.condition = 'Equals'

    indicator.add_observable(url)
    return indicator

def create_host_indicator(host_indicator):
    indicator = Indicator()
    indicator.title = 'Hostname of site hosting malware'
    indicator.add_indicator_type('Domain Watchlist')

    host = Hostname()
    host.value = host_indicator
    host.condition = 'Equals'

    indicator.add_observable(host)
    return indicator

def create_ip_indicator(ip_indicator):
    indicator = Indicator()
    indicator.title = 'IP address of site hosting malware'
    indicator.add_indicator_type('IP Watchlist')

    addr = Address(address_value=ip_indicator, category=Address.CAT_IPV4)
    addr.condition = 'Equals'

    indicator.add_observable(addr)
    return indicator

def parse_har(har_data):
    entries = list()
    for entry in har_data['log']['entries']:
        indicator_data = {'ip': entry['serverIPAddress']}
        indicator_data['url'] = entry['request']['url']
        for header in entry['request']['headers']:
            if header['name'] == 'Host':
                indicator_data['host'] = header['value']
        entries.append(indicator_data)
    return entries

description = 'Tool for parsing HAR file and generating MAEC and STIX IOC output'
parser = argparse.ArgumentParser(description=description)
parser.add_argument('har', metavar='HAR', help='Target HAR file')
args, unknown = parser.parse_known_args()

site_name = re.sub('\.har', '', args.har)

har_fh = open(args.har)
har_file = har_fh.read()
har_fh.close()
har_data = json.loads(har_file)

indicator_list = parse_har(har_data)

stix_indicators = list()
for entry in indicator_list:
    stix_indicators.append(create_url_indicator(entry['url']))
    stix_indicators.append(create_ip_indicator(entry['ip']))
    stix_indicators.append(create_host_indicator(entry['host']))

stix_package = init_stix()

for stix_indicator in stix_indicators:
    stix_package.add(stix_indicator)

working_dir = os.path.dirname(os.path.realpath(__file__))

maec_package = create_maec(indicator_list[0]['url'])

maec_out_file = os.path.join(working_dir, '{}.maec'.format(site_name))
maec_fh = open(maec_out_file, 'w')
maec_fh.write(maec_package.to_xml())
maec_fh.close()

stix_out_file = os.path.join(working_dir, '{}.stix'.format(site_name))
stix_fh = open(stix_out_file, 'w')
stix_fh.write(stix_package.to_xml())
stix_fh.close()
