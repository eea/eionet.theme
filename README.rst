eionet.plone.theme
========================

Theme package for eionet.europa.eu


Installation
------------

* Install ``eionet.plone.theme`` by adding it to your buildout:

::

    [buildout]
    ...
    eggs =
        ...
        eionet.theme

* And then running:

    ``bin/buildout``


Development
------------

``npm install``

For development mode, run:

``grunt watch``

For production mode, run:

``grunt``


Overrides
------------

Currently implemented overrides:

- path bar override so that the home breadcrumb is taken from portal_actions -> portal_tabs
- mail_password_template/form/response override to customize the forms and changed the view permisssion
  to cmf.ManagePortal so that they aren't accessible to the user. The eionet password_reset tool should
  be used for password reset
- added plone login_form/failsafe_login_form override in order to change the mail_password_url to the
  eionet password reset tool


Favicons
------------

The favicons are retrieved from the Plone site root, if you want to override them
add a favicons folder to your Plone site and replace the images


Contribute
----------

- Issue Tracker: https://github.com/eea/eionet.plone.theme/issues
- Source Code: https://github.com/eea/eionet.plone.theme


Support
-------

If you are having issues, please let us know.
