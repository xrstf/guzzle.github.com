====================
Service Descriptions
====================

Guzzle allows you to create commands for your web service client based on a document called a service description. As seen in :doc:`Building Web Service Clients </tour/building_services>`, Guzzle web service clients execute commands on a web service. Service descriptions make it easy to define a web service that can be consumed directly by a Guzzle client or used to produce documentation. Service description based clients are encouraged over creating concrete commands for every web service operation.

Creating a service description
------------------------------

Service descriptions can be representing using a PHP array or JSON document. Guzzle's service descriptions are heavily inspired by `Swagger <http://swagger.wordnik.com/>`_.

Let's say you're interacting with a web service called 'Foo' that allows for the following routes and methods::

    GET/POST   /users
    GET/DELETE /users/:id

The following JSON service description implements this simple web service:

.. code-block:: javascript

    {
        "name": "Foo",
        "apiVersion": "2012-10-14",
        "baseUrl": "http://api.foo.com",
        "description": "Foo is an API that allows you to Baz Bar",
        "operations": {
            "GetUsers": {
                "httpMethod": "GET",
                "uri": "/users",
                "summary": "Gets a list of users",
                "responseClass": "GetUsersOutput"
            },
            "CreateUser": {
                "httpMethod": "POST",
                "uri": "/users",
                "summary": "Creates a new user",
                "responseClass": "CreateUserOutput",
                "parameters": {
                    "name": {
                        "location": "json",
                        "type": "string"
                    },
                    "age": {
                        "location": "json",
                        "type": "integer"
                    }
                }
            },
            "GetUser": {
                "httpMethod": "GET",
                "uri": "/users/{id}",
                "summary": "Retrieves a single user",
                "responseClass": "GetUserOutput",
                "parameters": {
                    "id": {
                        "location": "uri",
                        "description": "User to retrieve by ID",
                        "required": true
                    }
                }
            },
            "DeleteUser": {
                "httpMethod": "DELETE",
                "uri": "/users/{id}",
                "summary": "Deletes a user",
                "responseClass": "DeleteUserOutput",
                "parameters": {
                    "id": {
                        "location": "uri",
                        "description": "User to delete by ID",
                        "required": true
                    }
                }
            }
        },
        "models": {
            "GetUsersOutput": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "location": "json",
                            "type": "string"
                        },
                        "age": {
                            "location": "json",
                            "type": "integer"
                        }
                    }
                }
            },
            "CreateUserOutput": {
                "type": "object",
                "properties": {
                    "id": {
                        "location": "json",
                        "type": "string"
                    },
                    "location": {
                        "location": "header",
                        "sentAs": "Location",
                        "type": "string"
                    }
                }
            },
            "GetUserOutput": {
                "type": "object",
                "properties": {
                    "name": {
                        "location": "json",
                        "type": "string"
                    },
                    "age": {
                        "location": "json",
                        "type": "integer"
                    }
                }
            },
            "DeleteUserOutput": {
                "type": "object",
                "properties": {
                    "status": {
                        "location": "statusCode",
                        "type": "integer"
                    }
                }
            }
        }
    }

If you attach this service description to a client, you would completely configure the client to interact with the Foo web service and provide valuable response models for each operation.

.. code-block:: php

    use Guzzle\Service\Description\ServiceDescription;

    $description = ServiceDescription::factory('/path/to/client.json');
    $client->setDescription($description);

    $command = $client->getCommand('DeleteUser', array('id' => 123));
    $responseModel = $client->execute($command);
    echo $responseModel['status'];

.. note::

    You can add the service description to your client's factory method or constructor.

Service description attributes
------------------------------

Service descriptions are comprised of the following top-level attributes:

+------------------+-----------------------------------------------------------------------------------------------------------------------+
| Attribute        | Description                                                                                                           |
+==================+=======================================================================================================================+
| name             | (optional) Name of the web service                                                                                    |
+------------------+-----------------------------------------------------------------------------------------------------------------------+
| apiVersion       | (optional) Version identifier that the service description is compatible with                                         |
+------------------+-----------------------------------------------------------------------------------------------------------------------+
| baseUrl/basePath | (optional) base URL of the service. Any relative URI in an operation will extend from the baseUrl                     |
+------------------+-----------------------------------------------------------------------------------------------------------------------+
| description      | Short summary of the web service                                                                                      |
+------------------+-----------------------------------------------------------------------------------------------------------------------+
| operations       | Hash of operations of the service. The key is the name of the operation and value is the attributes of the operation. |
+------------------+-----------------------------------------------------------------------------------------------------------------------+
| models           | Hash of models used by the service represented in JSON Schema format                                                  |
+------------------+-----------------------------------------------------------------------------------------------------------------------+
| includes         | (optional) Array of service description files to include and extend from (can be a .json, .js, or .php file)          |
+------------------+-----------------------------------------------------------------------------------------------------------------------+

baseUrl
~~~~~~~

The ``baseUrl`` attribute, aliased also as ``basePath``, can be used to add a custom baseUrl to a client when the service description is associated with the client. Some clients require custom logic to determine the baseUrl. In those cases, it is best to not include a baseUrl in the service description, but rather allow the factory method of the client to configure the client's baseUrl.

Any operation using a relative URI (e.g. /foo, baz/bar) will generate a URL that extends from the baseUrl attribute of the service description.

operations
~~~~~~~~~~

Operations are the actions that can be taken on a service. Each operation has a distinct endpoint and HTTP method. Operations are created and referenced by name. For example, if an API has a ``DELETE /users/:id`` operation, a satisfactory operation name might be ``DeleteUser`` with a parameter of ``id`` that is inserted into the URI.

Operations are comprised of the following attributes:

+------------------+-----------------------------------------------------------------------------------------------------------------------+
| Attribute        | Description                                                                                                           |
+==================+=======================================================================================================================+
| httpMethod       | (string) HTTP method used with the operation (e.g. GET, POST, PUT, DELETE, PATCH, etc)                                |
+------------------+-----------------------------------------------------------------------------------------------------------------------+
| uri              | (string) URI of the operation. The uri attribute can contain URI templates. The variables of the URI template are     |
|                  | parameters of the operation with a location value of ``uri``                                                          |
+------------------+-----------------------------------------------------------------------------------------------------------------------+
| class            | (string) Custom class to instantiate instead of the default ``Guzzle\Service\Command\OperationCommand``               |
+------------------+-----------------------------------------------------------------------------------------------------------------------+
| responseClass    | (string) This is what is returned from the method. Can be a primitive, PSR-0 compliant class name, or model name.     |
+------------------+-----------------------------------------------------------------------------------------------------------------------+
| responseNotes    | (string) Information about the response returned by the operation                                                     |
+------------------+-----------------------------------------------------------------------------------------------------------------------+
| responseType     | (string) One of 'primitive', 'class', 'model', or 'documentation'. If not specified, this value will be automatically |
|                  | inferred based on whether or not there is a model matching the name, if a matching PSR-0 compliant class name is      |
|                  | found, or set to 'primitive' by default.                                                                              |
+------------------+-----------------------------------------------------------------------------------------------------------------------+
| deprecated       | (bool) Set to true if this is a deprecated operation                                                                  |
+------------------+-----------------------------------------------------------------------------------------------------------------------+
| errorResponses   | (array) Errors that could occur when executing the command. Array of hashes, each with a 'code' (the HTTP response    |
|                  | code), 'phrase' (response reason phrase or description of the error), and 'class' (a custom exception class that      |
|                  | would be thrown if the error is encountered).                                                                         |
+------------------+-----------------------------------------------------------------------------------------------------------------------+
| data             | (array) Any extra data that might be used to help build or serialize the operation                                    |
+------------------+-----------------------------------------------------------------------------------------------------------------------+

parameters
^^^^^^^^^^

Parameters in both operations and models are represented using the `JSON schema <http://tools.ietf.org/id/draft-zyp-json-schema-03.html>`_ syntax.

+-----------------------+------------------------------------------------------------------------------------------------------+
| Name                  | Description                                                                                          |
+=======================+======================================================================================================+
| name                  | (string) Unique name of the parameter                                                                |
+-----------------------+------------------------------------------------------------------------------------------------------+
| type                  | (string|array) Type of variable (string, number, integer, boolean, object, array, numeric,           |
|                       | null, any). Types are using for validation and determining the structure of a parameter. You         |
|                       | can use a union type by providing an array of simple types. If one of the union types matches        |
|                       | the provided value, then the value is valid.                                                         |
+-----------------------+------------------------------------------------------------------------------------------------------+
| instanceOf:           | (string) When the type is an object, you can specify the class that the object must implement        |
+-----------------------+------------------------------------------------------------------------------------------------------+
| required              | (bool) Whether or not the parameter is required                                                      |
+-----------------------+------------------------------------------------------------------------------------------------------+
| default               | (mixed) Default value to use if no value is supplied                                                 |
+-----------------------+------------------------------------------------------------------------------------------------------+
| static                | (bool) Set to true to specify that the parameter value cannot be changed from the default            |
+-----------------------+------------------------------------------------------------------------------------------------------+
| description:          | (string) Documentation of the parameter                                                              |
+-----------------------+------------------------------------------------------------------------------------------------------+
| location              | (string) The location of a request used to apply a parameter. Custom locations can be registered     |
|                       | with a command, but the defaults are uri, query, header, body, json, xml, postField, postFile.       |
+-----------------------+------------------------------------------------------------------------------------------------------+
| sentAs                | (string) Specifies how the data being modeled is sent over the wire. For example, you may wish       |
|                       | to include certain headers in a response model that have a normalized casing of FooBar, but the      |
|                       | actual header is x-foo-bar. In this case, sentAs would be set to x-foo-bar.                          |
+-----------------------+------------------------------------------------------------------------------------------------------+
| filters               | (array) Array of static method names to to run a parameter value through. Each value in the          |
|                       | array must be a string containing the full class path to a static method or an array of complex      |
|                       | filter information. You can specify static methods of classes using the full namespace class         |
|                       | name followed by '::' (e.g. Foo\Bar::baz()). Some filters require arguments in order to properly     |
|                       | filter a value. For complex filters, use a hash containing a 'method' key pointing to a static       |
|                       | method, and an 'args' key containing an array of positional arguments to pass to the method.         |
|                       | Arguments can contain keywords that are replaced when filtering a value: '@value' is replaced        |
|                       | with the value being validated, '@api' is replaced with the Parameter object.                        |
+-----------------------+------------------------------------------------------------------------------------------------------+
| properties:           | When the type is an object, you can specify nested parameters                                        |
+-----------------------+------------------------------------------------------------------------------------------------------+
| additionalProperties: | (array) This attribute defines a schema for all properties that are not explicitly                   |
|                       | defined in an object type definition. If specified, the value MUST be a schema or a boolean. If      |
|                       | false is provided, no additional properties are allowed beyond the properties defined in the         |
|                       | schema. The default value is an empty schema which allows any value for additional properties.       |
+-----------------------+------------------------------------------------------------------------------------------------------+
| items                 | This attribute defines the allowed items in an instance array, and MUST be a schema or an array      |
|                       | of schemas. The default value is an empty schema which allows any value for items in the             |
|                       | instance array.                                                                                      |
|                       | When this attribute value is a schema and the instance value is an array, then all the items         |
|                       | in the array MUST be valid according to the schema.                                                  |
+-----------------------+------------------------------------------------------------------------------------------------------+
| pattern               | When the type is a string, you can specify the regex pattern that a value must match                 |
+-----------------------+------------------------------------------------------------------------------------------------------+
| enum                  | When the type is a string, you can specify a list of acceptable values                               |
+-----------------------+------------------------------------------------------------------------------------------------------+
| minItems              | (int) Minimum number of items allowed in an array                                                    |
+-----------------------+------------------------------------------------------------------------------------------------------+
| maxItems              | (int) Maximum number of items allowed in an array                                                    |
+-----------------------+------------------------------------------------------------------------------------------------------+
| minLength             | (int) Minimum length of a string                                                                     |
+-----------------------+------------------------------------------------------------------------------------------------------+
| maxLength             | (int) Maximum length of a string                                                                     |
+-----------------------+------------------------------------------------------------------------------------------------------+
| minimum               | (int) Minimum value of an integer                                                                    |
+-----------------------+------------------------------------------------------------------------------------------------------+
| maximum               | (int) Maximum value of an integer                                                                    |
+-----------------------+------------------------------------------------------------------------------------------------------+
| data                  | (array) Any additional custom data to use when serializing, validating, etc                          |
+-----------------------+------------------------------------------------------------------------------------------------------+
| format                | (string) Format used to coax a value into the correct format when serializing or unserializing.      |
|                       | You may specify either an array of filters OR a format, but not both.                                |
|                       | Supported values: date-time, date, time, timestamp, date-time-http                                   |
+-----------------------+------------------------------------------------------------------------------------------------------+
| $ref                  | (string) String referencing a service description model. The parameter is replaced by the            |
|                       | schema contained in the model.                                                                       |
+-----------------------+------------------------------------------------------------------------------------------------------+

location
^^^^^^^^

The location field of top-level parameters control how a parameter is serialized when generating a request.

- ``uri`` parameters are injected into any matching URI template value of an operation
- ``query`` parameters are injected into the query string of a request. Query values can be nested, which would result in a PHP style nested query string.
- ``header`` parameters are injected as headers on an HTTP request. Headers that are of type ``object`` will be added as multiple headers to a request using the key of the input array as the header key. Setting a ``sentAs`` attribute along with a type ``object`` will use the value of ``sentAs`` as a prefix for each header key.
- ``body`` parameters are injected as the body of a request. The input of these parameters may be anything that can be cast to a string or a ``Guzzle\Http\EntityBodyInterface`` object
- ``postField`` parameters are inserted as POST fields in a request. Nested values may be supplied.
- ``postFile`` parameters are added as POST files. A postFile value may be a string pointing to a local filename or a ``Guzzle\Http\Message\PostFileInterface`` object.
- ``json`` parameters flag a parameter as a top level key to add to a JSON object in the body. Nested values may be specified, with any number of nested ``Guzzle\Common\ToArrayInterface`` objects.
- ``xml`` parameters flag a parameter as a top level element to add to an XML document in the body.
- (no location): If a parameter has no location attribute, then the parameter is simply used as a data value.

.. note::

    Custom locations can be registered as new locations or override default locations if needed.

models
~~~~~~

Models are used in service descriptions to provide valuable output to an operation or to share snippets of JSON schemas throughout a service description. Models use the exact syntax and attributes used in parameters.

location
^^^^^^^^

The location field of top-level parameters in a model tell response parsers how date is retrieved from a response.

- ``statusCode``: Retrieves the status code of the response.
- ``reasonPhrase``: Retrieves the reason phrase of the response.
- ``header``: Retrieves a header value from a response.
- ``body``: Retrieves the body of the response
- ``json``: Retrieves a top-level parameter from a JSON response object.
- ``xml``: Retrieves a top-level node from an XML response

.. note::

    Custom locations can be registered as new locations or override default locations if needed.
