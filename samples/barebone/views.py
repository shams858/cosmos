import settings

import cosmos
from cosmos.service.auth import BasicLoginHandler

__author__ = 'Maruf Maniruzzaman'

import tornado
from tornado import gen
import json

from cosmos.service.requesthandler import RequestHandler


class IndexHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        try:
            with open(settings.INDEX_HTML_PATH) as f:
                self.write(f.read())
        except IOError as e:
            msg = """
File not found {}.
If you are developing cosmos create a local_settings.py file beside cosmosmain.py with following content:

import os

STATIC_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../adminpanel/app")
TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../adminpanel/templates")
INDEX_HTML_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../adminpanel/app/index.html")

            """.format(settings.INDEX_HTML_PATH)
            raise tornado.web.HTTPError(404, msg)


class LoginHandler(BasicLoginHandler):
    @gen.coroutine
    def get(self):
        next = self.get_argument("next", '/')
        try:
            with open(settings.LOGIN_HTML_PATH) as f:
                login_template = f.read()
                self._show_login_window(next, login_template=login_template)
        except IOError as e:
            raise tornado.web.HTTPError(404, "File not found")


class OAuth2DummyClientHandler(RequestHandler):
    @gen.coroutine
    def get(self, function):
        self.write(self.request.uri + " <br />" + function + "<br />")
        params = json.dumps({ k: self.get_argument(k) for k in self.request.arguments })
        self.write(params)
        pub_pem = self.settings.get("oauth2_public_key_pem")
        code = self.get_argument("code", "temp")
        token = self.get_argument("access_token", default=None)
        if token:
            header, claims = cosmos.auth.oauth2.verify_token(token, pub_pem, ['RS256'])
            self.write("<br /><hr />")
            self.write(json.dumps(header))
            self.write("<br /><hr />")
            self.write(json.dumps(claims))

        self.write("<br /><hr />")
        self.write("<a href='/tenant/oauth2/authorize/?response_type=code&state=mystate&resource=myresource.com/test&redirect_uri=/oauth2client/authorize/?tag=2'>Request Code</a><br />")
        self.write("<a href='/tenant/oauth2/token/?code={}&state=mystate&grant_type=code&redirect_uri=/oauth2client/authorize/?tag=2'>Request Token</a><br />".format(code))

        self.finish()


