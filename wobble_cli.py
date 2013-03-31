#!/usr/bin/env python
"""Wobble client.

Set the following environment variables:
WOBBLE_SERVER_URL <- optional
WOBBLE_USERNAME
WOBBLE_PASSWORD

Usage:
    wobble archive [-i <days>]

Options:
    -i --days-inactive=<days>   [default: 14]
"""
from __future__ import with_statement
from docopt import docopt
from os import environ
import datetime
from bs4 import BeautifulSoup
import logging

import sys
# add wobble lib
sys.path.append("./libs/wobble-client-python/")

from wobble import WobbleService


def enforce_credentials():
    if 'WOBBLE_USERNAME' not in environ:
        print "please configure a username as WOBBLE_USERNAME environment variable"
        sys.exit(1)
    if 'WOBBLE_PASSWORD' not in environ:
        print "please configure a password as WOBBLE_PASSWORD environment variable"
        sys.exit(1)


def archive_topics(days):
    try:
        try:
            wobble_service = WobbleService(api_endpoint=environ['WOBBLE_SERVER_URL'])
        except KeyError:
            wobble_service = WobbleService()

        with wobble_service.connect(environ['WOBBLE_USERNAME'],
                                    environ['WOBBLE_PASSWORD']) as service:
            today = datetime.date.today()
            threashhold = today - datetime.timedelta(days=int(days))

            topics = service.topics_list()

            for topic in topics['topics']:
                last_touch = datetime.datetime.fromtimestamp(topic['max_last_touch'])
                last_touch = last_touch.date()
                if last_touch < threashhold:
                    abstract = BeautifulSoup(topic['abstract']).get_text()
                    service.archive_topic(topic['id'])
                    logging.info("{}\tid:{}\t-> archived".format(
                                    abstract, topic['id']))

    except WobbleService.ProtocolError as e:
        print e.value


if __name__ == '__main__':
    args = docopt(__doc__)
    enforce_credentials()
    if args['archive']:
        archive_topics(args['--days-inactive'])
