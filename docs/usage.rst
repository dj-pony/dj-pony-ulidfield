=====
Usage
=====

To use DJ Pony ULID Field in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'dj_pony_ulidfield.apps.DjPonyULIDFieldConfig',
        ...
    )

Add DJ Pony ULID Field's URL patterns:

.. code-block:: python

    from dj_pony_ulidfield import urls as dj_pony_ulidfield_urls


    urlpatterns = [
        ...
        url(r'^', include(dj_pony_ulidfield_urls)),
        ...
    ]
