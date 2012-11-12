============
Installation
============

.. highlight:: php

Requirements
------------

#. PHP 5.3.2+ compiled with the cURL extension
#. A recent version of cURL 7.16.2+ compiled with OpenSSL and zlib

Installing Guzzle
-----------------

Composer
~~~~~~~~

Create composer.json file in the project root:

.. code-block:: json

    {
        "require": {
            "guzzle/guzzle": "3.0.*"
        }
    }

Then download composer.phar and run the install command:

.. code-block:: bash

    curl -s http://getcomposer.org/installer | php && ./composer.phar install
    
PEAR
~~~~

Guzzle can be installed through PEAR:

.. code-block:: bash

    pear -D auto_discover=1 install guzzlephp.org/pear/guzzle

Contributing to Guzzle
----------------------

In order to contribute, you'll need to checkout the source from GitHub and install Guzzle's dependencies using Composer:

.. code-block:: bash

    git clone https://github.com/guzzle/guzzle.git
    cd guzzle && curl -s http://getcomposer.org/installer | php && ./composer.phar install --dev

Guzzle is unit tested with PHPUnit. You will need to create your own phpunit.xml file in order to run the unit tests (or just copy phpunit.xml.dist to phpunit.xml). Run the tests using the vendored PHPUnit binary:

.. code-block:: bash

    vendor/bin/phpunit

You'll need to install node.js v0.5.0 or newer in order to test the cURL implementation.

Framework integrations
----------------------

Using Guzzle with Symfony
~~~~~~~~~~~~~~~~~~~~~~~~~

A `Guzzle Symfony2 bundle <https://github.com/ddeboer/GuzzleBundle>`_ is available on github thanks to `ddeboer <https://github.com/ddeboer>`_

Using Guzzle with Silex
~~~~~~~~~~~~~~~~~~~~~~~

A `Guzzle Silex service provider <https://github.com/guzzle/guzzle-silex-extension>`_ is available on github.
