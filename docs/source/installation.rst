Installation
============

Clone the git repository
------------------------

From the directory of your choice, run:

.. code-block:: bash

   git clone https://gitlab.e3d.rwth-aachen.de/cuypers/dynamic_lca_draft.git
   cd dynamic_lca_draft


Install dependencies
--------------------

The requirements:
.. literalinclude:: ../requirements.txt


Install from requirements.txt

.. code-block:: bash

    pip install -r requirements.txt


Building the documentation
--------------------------

From the project root directory you can run:

.. code-block:: bash

    cd docs
    make html

The generated html will be in "docs/_build/html".
Open the "docs/_build/html/index.html" file in your browser.