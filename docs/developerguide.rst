Developer's Guide
====================

This section provides a brief guideline for potential contributors. 


Adding parameters
------------------

To add the parameters to the configuration files


Adding Neuron Model
--------------------

Adding Synapse Model
---------------------

Updating the Documentation
---------------------------

Building the documentation locally 
````````````````````````````````````
Building the documentation locally is essential to test the modifications while preventing redundant pushes to the repository. Sphinx is well documented, yet we will provide the essentials for improving the documentation of the CxSystem. First, install the sphinx using:

.. code-block:: bash

   $ sudo apt-get install python-sphinx

When sphinx is installed, you can build the documentation using the following command:

.. code-block:: bash

   $ cd ./CxSystem/docs && make html 

The local documentation can then be find in *CxSystem/docs/_build/html/index.html*

Mocking modules
................

The auto-generated API using Sphinx tries to import the entire module hierarchy. This is not an issue when the document is built locally. However, not all the modules are available online in readthedocs website and therefore the online build will fail to generate the reference documentation. To address this issue, any imported module which is not part of the CxSystem must be added to *autodoc_mock_imports* list in CxSystem/docs/conf.py. 


