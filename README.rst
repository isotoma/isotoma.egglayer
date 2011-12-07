Python Egg Layer
================

This package provides python classes for building Python packages on the fly.
Why don't we use setuptools? Well we needed to generate the egg dynamically
from a Django view and not generate the temp files. Why on earth would you want
to dynamically generate a python package? Policy is really best injected into
Plone through GenericSetup. But a lot of the policy depends on settings in
Buildout or other deployment systems. Simple python eggs are trivial to
generate, so we decided to see how well it worked to generate policy eggs from
our configuration management tools.


Features
--------

Automatic namespacing
    If your package is called foo.bar.baz then foo/__init__.py and foo/bar/__init__.py will automatically contain the ``pkg_resources`` magic needed for namespacing, and the setup.py will define all the namespace packages.
Automatic z3c.autoinclude
    If you build a Plone package, it will automatically be advertised to Plone using z3c.autoinclude.


Hello, world!
-------------

Before we can start building an egg we need 3 things: The package name, version
and a file-like object to write to. This can be StringIO, a file or even a
Django HTTPResonse::

    from isotoma.egglayer import Package
    p = Package(open("test.zip", "w"), "test.package", "1.0")

You don't need to worry about directories. You just add files::

    p.add("test/package/__init__.py", "print 'Hello, world!'")

Any files you add are tracked so that the SOURCES.txt for the egg is correct.

When you have finished adding content to the package you call the close()
method. This will generate the egg-info directory and a setup.py::

    p.close()

Python will automatically call ``close()`` during ``__del__`` if you do not.


Dynamically generating packages from Django
-------------------------------------------

We set up a new view subclass like this::

    from django.views.generic import View
    from django.http import HttpResponse
    from django import template
    from isotoma.egglayer import Package

    class MyCustomizedEgg(View):

        def get(self, request, *args, **kwargs):
            response = HttpResponse(content_type="application/zip")
            response['Cache-Control'] = 'no-cache'
            response['Content-Disposition'] = 'filename=test.customegg-1.0.zip'

            p = Package(response, 'test.customegg', '1.0')
            p.add("test/customegg/foo.py", "print "hello world")
            p.close()

            return response


Because a ``HttpResonse`` is a file like object we can wire it up directly as
the output of the Package object. You can set a ``Cache-Control`` header to
stop the egg being cached while you are testing, but your final code shouldn't
require it. The ``Content-Disposition`` header allows your browser to suggest a
sensible filename when saving your dynamically generated package. If you are
using this view from a tool like pip or buildout it may or may not care about
this header.

(Obviously you will need to wire this into urls.py - see the wonderful Django
documentation for how to do this).

