================================================
Consuming web services using web service clients
================================================

.. highlight:: php

Guzzle's awesome HTTP support provides the raw materials needed to build robust web service clients. Guzzle's service
layer provides the glue needed to bring it all together.

Command based web service clients
---------------------------------

Command based web service clients help to hide the underlying implementation of an API by following the
`command pattern <http://en.wikipedia.org/wiki/Command_pattern>`_ and giving a concrete class or service description
to each operation that can be made on a web service.

Instantiating web service clients using a ServiceBuilder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The best way to instantiate Guzzle web service clients is to let Guzzle handle building the clients for you using a
ServiceBuilder. A ServiceBuilder is responsible for creating concrete client objects based on configuration settings
and helps to manage credentials for different environments.

A ServiceBuilder can source information from an array, an PHP include file that returns an array, or a JSON file::

    use Guzzle\Service\Builder\ServiceBuilder;

    // Source service definitions from a JSON file
    $builder = ServiceBuilder::factory('services.json');

Clients are referenced using a customizable name you provide in your service definition. The ServiceBuilder is a sort
of multiton object-- it will only instantiate a client once and return that client for subsequent retrievals. You can
get a "throwaway" client (a client that is not persisted by the ServiceBuilder) by passing ``true`` in the second
argument of ``ServiceBuilder::get()``.

Here's an example of retrieving an Unfuddle client from your ServiceBuilder::

    $client = $builder->get('unfuddle');
    // You can also use the ServiceBuilder object as an array
    $client = $builder['unfuddle'];

Sourcing data from an array
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Parameters need to be specified in each ``<service>`` element to tell a ``Guzzle\Service\Builder\ServiceBuilder``
object how to build the web service client. Clients are given names which are handy for using multiple accounts for
the same service or creating development clients vs. production clients.

.. code-block:: php

    $services = array(
        'includes' => array(
            '/path/to/other/services.json',
            '/path/to/other/php_services.php'
        ),
        'services' => array(
            'abstract.foo' => array(
                'params' => array(
                    'username' => 'foo',
                    'password' => 'bar'
                )
            ),
            'bar' => array(
                'extends' => 'abstract.foo',
                'class'   => 'MyClientClass',
                'params'  => array(
                    'other' => 'abc'
                )
            )
        )
    );

A service builder configuration array contains two top-level array keys:

* includes: Array of paths to JSON or PHP include files to include in the configuration.
* services: Associative array of defined services that can be created by the service builder. Each service can contain
the following keys:
    * class: The concrete class to instantiate that implements the ``Guzzle\Common\FromConfigInterface``.
    * extends: The name of a previously defined service to extend from
    * params: Associative array of parameters to pass to the factory method of the service it is instantiated

The first client defined, ``abstract.foo``, is used as a placeholder of shared configuration values. Any service
extending abstract.foo will inherit its params. As an example, this can be useful when clients share the same username
and password.

The next client, ``bar``, extends from ``abstract.foo`` using the ``extends`` attribute referencing the client from
which to extend. Additional parameters can be merged into the original service definition when extending a parent
service. Each client that you intend to instantiate must specify a ``class`` attribute that references the full class
name of the client being created.

Sourcing from a PHP include
^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can create service builder configurations using a PHP include file. This can be useful if you wish to take
advantage of an opcode cache like APC to speed up the process of loading and processing the configuration. The PHP
include file is the same format as an array, but you simply create a PHP script that returns an array and save the
file with the .php file extension::

    <?php return array('services' => '...');
    // Saved as config.php

This configuration file can then be used with a service builder::

    $builder = ServiceBuilder::factory('config.php');

Sourcing from a JSON document
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can use JSON documents to serialize your service descriptions. The JSON format uses the exact same structure as
the PHP array syntax, but it's just serialized using JSON.

.. code-block:: javascript

    {
        "includes": ["/path/to/other/services.json", "/path/to/other/php_services.php"],
        "services": {
            "abstract.foo": {
                "params": {
                    "username": "foo",
                    "password": "bar"
                }
            },
            "bar": {
                "extends": "abstract.foo",
                "class": "MyClientClass",
                "params": {
                    "other": "abc"
                }
            }
        }
    }

Referencing other clients in parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If one of your clients depends on another client as one of its parameters, you can reference that client by name by
enclosing the client's reference key in ``{}``.

.. code-block:: javascript

    {
        "services": {
            "token": {
                "class": "My\Token\TokenFactory",
                "params": {
                    "access_key": "xyz"
                }
            },
            "client": {
                "class": "My\Client",
                "params": {
                    "token_client": "{token}",
                    "version": "1.0"
                }
            }
        }
    }

When ``client`` is constructed by the service builder, the service builder will first create the ``token`` service
and then inject the token service into ``client``'s factory method in the ``token_client`` parameter.

Using Client objects
--------------------

Web service clients are the central point of interaction with a web service. They hold service configuration data and
help to ready HTTP requests to be sent to a web service. Web service clients don't know much about the service
itself-- they just create requests and execute commands. Configuration settings can be retrieved from a client by
passing a configuration key to the ``getConfig()`` method of a client
(e.g. ``$token = $client->getConfig('devpay_product_token')``).

Client's can contain special options that alter the behavior of the client (including the options available to
``Guzzle\Http\Client``):

* command.params: Associative array of parameters to set on every command created by the client

Executing commands using a client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Commands are used to take action on a web service and format the response from the web service into something useful.

Commands can be instantiated and configured by a client by calling the ``getCommand()`` method on a client and using
the command's name.

By default, a client will attempt to find concrete command classes using the short form of a command's name. This is
calculated based on the folder hierarchy of a command and converting the CamelCased named commands into snake_case.
Here are some examples on how the command names are calculated:

#. ``Foo\Command\JarJar`` **->** jar_jar
#. ``Foo\Command\Test`` **->** test
#. ``Foo\Command\People\GetCurrentPerson`` **->** people.get_current_person

Notice how any sub-namespace beneath ``Command`` is converted from ``\`` to ``.`` (a period). CamelCasing is converted
to lowercased snake_casing (e.g. JarJar == jar_jar).

Here's how you would get the Foo client from the ServiceBuilder and execute a JarJar command::

    // Retrieve the client by name
    $client = $serviceBuilder['foo'];

    $command = $client->getCommand('jar_jar');
    $result = $client->execute($command);
    $result = $client->getResult();
    $httpResponse = $command->getResponse();
    $httpRequest = $command->getRequest();

You can take some shortcuts in your code by passing key-value pair arguments to a command when grabbing it from the client::

    $result = $client->getCommand('jar_jar', array('mesa' => 'address_senate'))->execute();

.. note::

    The format and notation used to retrieve commands from a client can be customized by injecting a custom command
    factory, ``Guzzle\Service\Command\Factory\FactoryInterface``, on the client using
    ``$client->setCommandFactory()``.

Special command options
^^^^^^^^^^^^^^^^^^^^^^^

Command results can contain various types based on the command's implementation. Some commands might set the result to
a Response object, some might use an array, SimpleXMLElement, or ``Guzzle\Service\Resource\Model``. Check the client's
documentation or service description to see what the result format of a particular operation will be. To some extent,
you can control the behavior of a command and what return types are created for a command by setting special options
on the command. Any command that extends from ``Guzzle\Service\Command\AbstractCommand`` should honor these values.

* command.headers: Associative array of headers to send with the request created by the command
* command.on_complete: Function to execute when the command successfully completes. The function should accept a
  command object.
* command.disable_validation: Set to true to disable validation of the schema of the command against the input data.
  Note: some validations also perform transformations and filtering, so this may break your client. This should only
  be used in a controlled script to squeeze out more performance
* command.response_processing: Alters how results are processed. Can be set to one of:
    * raw: Does not processing on the result and the result will simply be a ``Guzzle\Http\Message\Response`` object.
    * native: Will convert JSON responses into arrays and XML responses into SimpleXMLElement objects.
    * model: Will attempt to use the associated responseClass model of the operation and the result will be a
      ``Guzzle\Service\Resource\Model`` object. This is the default setting, and if no model is found, Guzzle
      attempts to return a native response. If no native response can be used, then Guzzle will set the result to
      raw response.

.. note::

    Understand that changing how inputs are validated and how results are processed removes all guarantees that higher
    level abstractions like iterators and batching will still work.

Executing commands in parallel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Commands can be sent in parallel by executing an array of commands with a client::

    $client = $serviceBuilder['foo'];

    foreach ($client->execute(array(
        $client->getCommand('jar_jar', array('domain' => 'test')),
        $client->getCommand('test'),
        $client->getCommand('people.get_current_person')
    )) as $command) {
        echo $command->getName() . ': ' . $command->getResponse()->getStatusCode() . "\n";
    }

.. note::

    All commands executed from a client using an array must originate from the same client.

Next steps
~~~~~~~~~~

Check the documentation of the web service client you are using to see the available commands and operations of the
client.
