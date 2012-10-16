============
Installation
============

.. highlight:: php

Requirements
------------

#. PHP 5.3.2+ compiled with the cURL extension
#. A recent version of cURL 7.16.2+ compiled with OpenSSL and zlib
#. `PHPUnit <http://www.phpunit.de/manual/3.6/en/installation.html>`_ is required to run the unit tests
#. `node.js <http://nodejs.org>`_ is required to run the unit tests
#. `Phing <http://www.phing.info/trac/>`_ is required to run the build scripts

Installing Guzzle
-----------------

Composer
~~~~~~~~

Create composer.json file in the project root:

.. code-block:: javascript

    {
        "require": {
            "guzzle/guzzle": "3.0.*"
        }
    }

Then download composer.phar and run the install command:

.. code-block:: bash

    curl -s http://getcomposer.org/installer | php && ./composer.phar install

Github
~~~~~~

Guzzle can be installed from source by cloning the Guzzle GitHub repository and installing the dependencies using composer:

.. code-block:: bash

    git clone https://github.com/guzzle/guzzle.git
    cd guzzle
    curl -s http://getcomposer.org/installer | php && ./composer.phar install --dev

PEAR
~~~~

Guzzle can be installed through PEAR

.. code-block:: bash

    pear channel-discover guzzlephp.org/pear
    pear install guzzle/guzzle

Running the unit tests
----------------------

Guzzle is unit tested with PHPUnit. You will need to create your own phpunit.xml file in order to run the unit tests. You can customize this file to suit your testing needs:

.. code-block:: bash

    cp phpunit.xml.dist phpunit.xml
    phpunit

You will need to install node.js v0.5.0 or newer in order to test the cURL implementation.

Framework integrations
----------------------

Using Guzzle with Symfony
~~~~~~~~~~~~~~~~~~~~~~~~~

A `Guzzle Symfony2 bundle <https://github.com/ddeboer/GuzzleBundle>`_ is available on github thanks to `ddeboer <https://github.com/ddeboer>`_

Using Guzzle with Silex
~~~~~~~~~~~~~~~~~~~~~~~

A `Guzzle Silex service provider <https://github.com/guzzle/guzzle-silex-extension>`_ is available on github.
