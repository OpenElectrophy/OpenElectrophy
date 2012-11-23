=================
Developers' guide
=================


Getting the source code
-----------------------

We use the Git version control system. The best way to contribute is through
GitHub_. You will first need a GitHub account, and you should then fork the
repository at https://github.com/OpenElectrophy/OpenElectrophy
(see http://help.github.com/fork-a-repo/).

To get a local copy of the repository::

    $ cd /some/directory
    $ git clone git@github.com:<username>/OpenElectrophy/OpenElectrophy.git

Do not install OpenElectrophy but use qn alternate solution with the *develop* option, this avoids
reinstalling when there are changes in the code::

    $ sudo python setup.py develop

To update to the latest version from the repository::

    $ git pull

Working on the documentation
----------------------------

The documentation is written in `reStructuredText`_, using the `Sphinx`_
documentation system. To build the documentation::

    $ cd python-neo/doc
    $ make html
    
Then open `some/directory/neo_trunk/doc/build/html/index.html` in your browser.

Committing your changes
-----------------------

Once you are happy with your changes, **run the test suite again to check
that you have not introduced any new bugs**. Then you can commit them to your
local repository::

    $ git commit -m 'informative commit message'
    
If this is your first commit to the project, please add your name and
affiliation/employer to :file:`doc/source/authors.rst`

You can then push your changes to your online repository on GitHub::

    $ git push
    
Once you think your changes are ready to be included in the main Neo repository,
open a pull request on GitHub (see https://help.github.com/articles/using-pull-requests).


Making a release
----------------


First check that the version string (in :file:`OPenElectrophy/version.py`)

To build a source package::

    $ python setup.py sdist

To upload the package to `PyPI`_ (currently Samuel Garcia, Nicolas Fourcaut-Trocmé and CHros Rodger
have the necessary permissions to do this)::

    $ python setup.py sdist upload
    $ python setup.py upload_docs --upload-dir=doc/build/html

Finally, tag the release in the Git repository::

    $ git tag <version>




.. _PEP394: http://www.python.org/dev/peps/pep-0394/
.. _PyPI: http://pypi.python.org
.. _GitHub: http://github.com