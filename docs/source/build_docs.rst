.. _build_docs:

Building the docs
=================

The project's documentation is built using Sphinx and hosted on Read The Docs.

Generating API documentation
----------------------------

The documentation in docstrings has to be "converted" to .rst files using autodoc before the documentation can be built:

.. code-block:: sh

        sphinx-apidoc -o  docs/source hashtablebot

Building the docs
-----------------
To generate the documentation's html files, use the following:

.. code-block:: sh

        sphinx-build -b html docs/source/ docs/build/html

ReadTheDocs deployment
------------------------
The docs are deployed automatically when the main branch is updated.

