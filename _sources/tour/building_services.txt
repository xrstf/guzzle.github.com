============================
Building web service clients
============================

.. highlight:: php

Building web service clients using commands and :doc:`service description </guide/service/service_descriptions>` is better than creating requests manually. A command-based web service client that abstracts away the HTTP request and response makes a client more future-proof; if the API you are interacting with changes (for example, adds a required field), then you would only have to update the command in one place rather than every single file in your project that interacts with the web service. Guzzle uses the `command pattern <http://en.wikipedia.org/wiki/Command_pattern>`_ for building requests and processing responses. Abstracting the underlying implementation helps new developers to quickly send requests to an API using any of the best-practices coded into the command itself, rather than assuming that every developer on your team has an intricate understanding of the web service.

Setting up
----------

The first thing you will need to do is create the directory structure of your project. The directory structure should resemble the following (of course substituting FooBar for your web service client's name):

.. code-block:: none

    ./src/FooBar/
    ├── FooBarClient.php
    ├── service.php
    ├── Command/
    │   ├── CommandName.php
    ├── tests/
    │   ├── mock/
    |   ├── FooBar/
    |   |   ├── Tests/
    |   |   |   ├── Command/
    |   |   |   |   └── CommandNameTest.php
    |   |   └── FooBarClientTest.php
    |   └── bootstrap.php

+--------------------------------------+---------------------------------------------------------------------------------------------------------------------+
| src/FooBar/Command/                  | Place all of the concrete commands for your web service in this folder (note: you might not need any).              |
+--------------------------------------+---------------------------------------------------------------------------------------------------------------------+
| src/FooBar/service.php               | This optional file can contain the :doc:`service description </guide/service/service_descriptions>` of your client. |
+--------------------------------------+---------------------------------------------------------------------------------------------------------------------+
| src/FooBar/FooBarClient.php          | Rename this class to the CamelCase name of the web service you are implementing followed by ``Client``. A good      |
|                                      | client name would be something like ``FooBarClient.php``.                                                           |
+--------------------------------------+---------------------------------------------------------------------------------------------------------------------+
| tests/                               | Place your ``bootstrap.php`` file in this folder. The boostrap.php file is responsible for setting up PHPUnit       |
|                                      | tests.                                                                                                              |
+--------------------------------------+---------------------------------------------------------------------------------------------------------------------+
| tests/mock                           | Place mock response files in this folder. Mock response files include HTTP response headers and the entity body     |
|                                      | of a response. Keep each HTTP response in a separate file.                                                          |
+--------------------------------------+---------------------------------------------------------------------------------------------------------------------+

Create a client
---------------

In order for a ServiceBuilder to create your client using a parameterized array, you'll need to implement a static ``factory()`` method that maps an array of parameters into an instantiated client object. It should be possible to instantiate most if not all collaborators that would normally be injected into a client in your client's `static factory method <http://twofoos.org/content/static-factory-methods/>`_. This method is used to create a client using a simple, key value pair array so that the client can easily be configured, utilize default configuration settings, provide simplified validation, and can easily be serialized into various configuration formats.

A common pattern among Guzzle clients is to provide a constructor that accepts arguments containing all of the required collaborators of a client, while the factory method can translate simple key value pair data into instantiated collaborators that are then passed to the client's constructor. This allows end users to instantiate your client using an array or configuration file while still allowing the client to be easily tested.

.. note::

    Your client will not work with a service builder if you do not create a static factory method.

Let's start get started on our client. First we will extend the ``Guzzle\Service\Client`` class. Next we will create a static factory method used to instantiate the client. The factory method accepts parameters, adds default parameters, validates that required parameters are present, creates a new client, attaches any observers needed for the client, and returns the client object. Most simple clients wont need a custom constructor, but feel free to add one to your client if it requires additional collaborators (e.g. a special signature or region object)::

    namespace MyService;

    use Guzzle\Common\Collection;
    use Guzzle\Service\Client;
    use Guzzle\Service\Description\ServiceDescription;

    /**
     * My example web service client
     */
    class MyServiceClient extends Client
    {
        /**
         * Factory method to create a new MyServiceClient
         *
         * The following array keys and values are available options:
         * - base_url: Base URL of web service
         * - scheme:   URI scheme: http or https
         * - username: API username
         * - password: API password
         *
         * @param array|Collection $config Configuration data
         *
         * @return self
         */
        public static function factory($config = array())
        {
            $default = array(
                'base_url' => '{scheme}://{username}.test.com/',
                'scheme'   => 'https'
            );
            $required = array('username', 'password', 'base_url');
            $config = Collection::fromConfig($config, $default, $required);

            $client = new self($config->get('base_url'), $config);
            // Attach a service description to the client
            $description = ServiceDescription::factory(__DIR__ . '/client.php');
            $client->setDescription($description);

            return $client;
        }
    }

The ``Collection::fromConfig`` method is responsible for adding default parameters to a configuration object and ensuring that required parameters are in the configuration. The static factory method in the above example will be very similar to the code you will need in your client's factory method. Any object composition required to build the client should be added in the factory method (for example, attaching event observers to the client based on configuration settings).

Commands
--------

Commands can be created in one of two ways: create a concrete command class that extends ``Guzzle\Service\Command\AbstractCommand`` or :doc:`create an OperationCommand based on a service description </guide/service/service_descriptions>`. The recommended approach is to use a service description to define your web service, but use concrete commands when custom logic must be implemented for marshaling or unmarshaling an HTTP message.

Commands are the method in which you abstract away the underlying format of the requests that need to be sent to take action on a web service. Commands in Guzzle are meant to be built by executing a series of setter methods on a command object. Commands are only validated when they are being executed. A ``Guzzle\Service\Client`` object is responsible for executing commands. Commands created for your web service must implement ``Guzzle\Service\Command\CommandInterface``, but it's easier to extend the ``Guzzle\Service\Command\AbstractCommand`` class and implement the ``build()`` method, and optionally the ``process()`` method.

The ``build()`` method of a command is responsible for using the arguments of the command to build a HTTP request and set the request on the $request property of the command object. This step is usually taken care of for you when using a service description driven command that uses the default ``Guzzle\Service\Command\OperationCommand``. You may wish to implement the process method yourself when you aren't using a service description or need to implement a more complex command. When implementing a custom build method, be sure to set the class property of ``$this->request`` to an instantiated and ready to send request.

The ``process()`` method of a command is responsible for converting an HTTP response into something more useful. For example, a service description operation that has specified a model object in the ``responseClass`` attribute of the operation will set a ``Guzzle\Service\Resource\Model`` object as the result of the command. This behavior can be completely modified as needed-- even if you are using operations and responseClass models. Simply implement a custom ``process()`` method that sets the ``$this->result`` class property to whatever you choose. You can reuse parts of the default Guzzle response parsing functionality or get inspiration from existing code by using ``Guzzle\Service\Command\OperationResponseParser`` and ``Guzzle\Service\Command\DefaultResponseParser`` classes.

Operations
----------

Operations are owned by commands to describe the operation, including acceptable parameters, the result of the command, the operation name, HTTP method, description of the operation, etc.. Operations are automatically associated with a command object when using a service description driven client.

When not using a service description, it is not necessary to create and associate a ``Guzzle\Service\Description\OperationInterface`` object with a command, but it is highly encouraged because it makes commands and their capabilities more discoverable. A default operation object containing almost no information is instantiated by default when using the ``Guzzle\Service\Command\AbstractCommand``. You can create and use a customized operation object with a command by extending the ``createOperation`` method of the AbstractCommand and returning an instantiated ``Guzzle\Service\Description\OperationInterface`` object.

Information on creating service descriptions and defining operations can be found in the :doc:`service description </guide/service/service_descriptions>` chapter.

Iterating over resources
------------------------

Web services often implement pagination in their responses. Users of your web service client should not be responsible for implementing the logic involved in iterating through pages of results. Guzzle provides a simple resource iterator foundation to make it easier on web service client developers to offer a useful abstraction layer.

See the guide on :doc:`Resource Iterators </guide/service/resource_iterators>` for more information on creating resource iterators for your client.

Batch operations
----------------

Some web services provide special operations used to perform operations in bulk. For example, a service might allow you to delete a single object at a time using the DELETE method, but allows you to delete multiple objects by sending a single POST request with a body specifying the objects to delete. In situations like this, you should consider implementing custom batching objects to provide a simple way for your users to benefit from the performance increase without needing to implement must custom code in their applications.

See the guide on :doc:`Batching </guide/batching>` for more information on creating custom batching strategies for your client.

Unit test your service
----------------------

Unit testing a Guzzle web service client is not very difficult thanks to some of the freebies you get from the ``Guzzle\Tests`` namespace. You can set mock responses on your requests or send requests to the test node.js server that comes with Guzzle.

You can learn more about unit testing guzzle web service clients by reading the :doc:`Unit testing web service clients </guide/service/testing_clients>` guide.
