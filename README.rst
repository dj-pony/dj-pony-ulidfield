=============================
DJ Pony ULID Field
=============================

.. image:: https://badge.fury.io/py/dj-pony.ulidfield.svg
    :target: https://badge.fury.io/py/dj-pony.ulidfield

.. image:: https://travis-ci.org/techdragon/dj-pony.ulidfield.svg?branch=master
    :target: https://travis-ci.org/techdragon/dj-pony.ulidfield

.. image:: https://codecov.io/gh/techdragon/dj-pony.ulidfield/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/techdragon/dj-pony.ulidfield

A ULID Field for Django that does all the work for you.

Documentation
-------------

The full documentation is at https://dj-pony-ulidfield.readthedocs.io.

Quickstart
----------

Install DJ Pony ULID Field::

    pip install dj-pony.ulidfield

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'dj_pony.ulidfield.apps.DjPonyULIDFieldConfig',
        ...
    )

Add DJ Pony ULID Field's URL patterns:

.. code-block:: python

    from dj_pony.ulidfield import urls as dj_pony_ulidfield_urls


    urlpatterns = [
        ...
        url(r'^', include(dj_pony_ulidfield_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
