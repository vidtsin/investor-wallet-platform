# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

import requests
from lxml import html
from odoo.tests.common import HttpCase

import odoo

HOST = "127.0.0.1"
PORT = odoo.tools.config["http_port"]
_logger = logging.getLogger(__name__)


def build_url(url):
    return "http://%s:%s%s" % (HOST, PORT, url)


class TestIWPBase(HttpCase):
    def setUp(self):
        super(TestIWPBase, self).setUp()
        self.session = requests.Session()

    @staticmethod
    def html_doc(response):
        """Get an HTML LXML document."""
        return html.fromstring(response.content)

    def get_csrf_token(self, response):
        doc = self.html_doc(response)
        token = doc.xpath("//input[@name='csrf_token']")[0].get("value")
        if token:
            return token
        else:
            raise ValueError("No csrf token in response")

    def login(self, login, password):
        url = "/web/login"
        res = self.http_get(url)
        doc = self.html_doc(res)
        token = doc.xpath("//input[@name='csrf_token']")[0].get("value")
        return self.http_post(
            url=url,
            data={"login": login, "password": password, "csrf_token": token},
        )

    def http_get(self, url):
        if url.startswith("/"):
            url = "http://%s:%s%s" % (HOST, PORT, url)
        return self.session.get(url)

    def http_post(self, url, data):
        if url.startswith("/"):
            url = "http://%s:%s%s" % (HOST, PORT, url)
        return self.session.post(url, data=data)
