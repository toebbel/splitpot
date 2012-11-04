# -*- encoding: UTF-8 -*-
#
# Form based authentication for CherryPy.
# Requires Session tool to be loaded.
#

import cherrypy
from utils.Auth import check_credentials, CURRENT_USER_NAME

from mako.template import Template
from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['template/', 'template/auth/'])


class AuthController(object):
    """
    Controller to provide login and logout actions
    """

    def get_loginform(self, username, msg="Enter login information", from_page="/"):
      tmpl = lookup.get_template("login.html")
      return tmpl.render(username = username, msg = msg, from_page = from_page)


    @cherrypy.expose
    def login(self, username=None, password=None, from_page="/"):
        """
        Checks the login data against utils/auth. redirects to from_page or to "/" after successfull login
        """
        if username is None or password is None:
            return self.get_loginform("", from_page=from_page)

        error_msg = check_credentials(username, password)
        if error_msg:
            return self.get_loginform(username, error_msg, from_page)
        else:
            cherrypy.session[CURRENT_USER_NAME] = cherrypy.request.login = username
            raise cherrypy.HTTPRedirect(from_page or "/")


    @cherrypy.expose
    def logout(self, from_page="/"):
        """
        Destroys complete Session and redirects to about page or from_page, if given
        """
        sess = cherrypy.session
        username = sess.get(CURRENT_USER_NAME, None)
        sess[CURRENT_USER_NAME] = None
        if username:
            cherrypy.request.login = None
        raise cherrypy.HTTPRedirect(from_page or "/about")
