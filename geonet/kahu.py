# geonet.kahu
# Interaction with the Kahu replica management service.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Thu Jun 14 07:16:43 2018 -0400
#
# ID: kahu.py [] benjamin@bengfort.com $

"""
Interaction with the Kahu replica management service.
"""

##########################################################################
## Imports
##########################################################################

import requests

from urlparse import urljoin
from geonet.config import settings


##########################################################################
## Kahu API Wrapper
##########################################################################

class Kahu(object):
    """
    Methods for accessing the Kahu API service.
    """

    ENDPOINTS = {
        "status": "/api/status/",
        "replicas-list": "/api/replicas/",
        "replicas-tokens": "/api/replicas/tokens/",
        "replicas-geonet": "/api/replicas/geonet/",
    }

    def __init__(self, url=None, api_key=None):
        self.base_url = url or settings.kahu.url
        self.api_key = api_key or settings.kahu.api_key

    def status(self):
        res = requests.get(
            self.get_endpoint("status"), headers=self.get_headers()
        )
        res.raise_for_status()
        return res.json()

    def replicas(self):
        url = self.get_endpoint("replicas-list")
        res = requests.get(url, headers=self.get_headers())
        res.raise_for_status()
        return res.json()

    def tokens(self):
        url = self.get_endpoint("replicas-tokens")
        res = requests.get(url, headers=self.get_headers())
        res.raise_for_status()
        return res.json()

    def activate(self, replicas):
        url = self.get_endpoint("replicas-geonet")
        res = requests.post(url, headers=self.get_headers(), json=replicas)
        res.raise_for_status()
        return res.json()

    def create_replica(self, data):
        url = self.get_endpoint("replicas-list")
        res = requests.post(url, headers=self.get_headers(), json=data)

        if res.status_code >= 200 and res.status_code < 300:
            return res.json(), True

        if res.status_code == 400:
            return res.json(), False

        # Raise an exception if we could not return
        res.raise_for_status()
        raise Exception(
            "unknown status response: {} from Kahu".format(res.status_code)
        )

    def get_headers(self):
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.api_key),
        }

    def get_endpoint(self, name):
        return urljoin(self.base_url, self.ENDPOINTS[name])

    def get_detail_endpoint(self, name, pk):
        return urljoin(self.base_url, self.ENDPOINTS[name], pk)
