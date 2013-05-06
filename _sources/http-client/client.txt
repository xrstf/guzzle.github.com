======================
The Guzzle HTTP client
======================

Guzzle gives PHP developers complete control over HTTP requests while utilizing HTTP/1.1 best practices. Guzzle's HTTP
functionality is a robust framework built on top of the `PHP libcurl bindings <http://www.php.net/curl>`_.

The three main parts of the Guzzle HTTP client are:

+--------------+-------------------------------------------------------------------------------------------------------+
| Clients      | ``Guzzle\Http\Client`` (creates and sends requests, associates a response with a request)             |
+--------------+-------------------------------------------------------------------------------------------------------+
| Requests     | ``Guzzle\Http\Message\Request`` (requests with no body),                                              |
|              | ``Guzzle\Http\Message\EntityEnclosingRequest`` (requests with a body)                                 |
+--------------+-------------------------------------------------------------------------------------------------------+
| Responses    | ``Guzzle\Http\Message\Response``                                                                      |
+--------------+-------------------------------------------------------------------------------------------------------+

Creating a Client
-----------------

Clients create requests, send requests, and set responses on a request object. When instantiating a client object,
you can pass an optional "base URL" and optional array of configuration options. A base URL is a
:ref:`URI template <uri-templates>` that contains the URL of a remote server. When creating requests with a relative
URL, the base URL of a client will be merged into the request's URL.

.. code-block:: php

    use Guzzle\Http\Client;

    // Create a client and provide a base URL
    $client = new Client('https://api.github.com');

    $request = $client->get('/user');
    $request->setAuth('user', 'pass');
    echo $request->getUrl();
    // >>> https://api.github.com/user

    // You must send a request in order for the transfer to occur
    $response = $request->send();

    echo $response->getBody();
    // >>> {"type":"User", ...

    echo $response->getHeader('Content-Length');
    // >>> 792

    $data = $response->json();
    echo $data['type'];
    // >>> User

Base URLs
~~~~~~~~~

Notice that the URL provided to the client's ``get()`` method is relative. Relative URLs will always merge into the
base URL of the client. There are a few rules that control how the URLs are merged.

.. tip::

    Guzzle follows `RFC 3986 <http://tools.ietf.org/html/rfc3986#section-5.2>`_ when merging base URLs and
    relative URLs.

In the above example, we passed ``/user`` to the ``get()`` method of the client. This is a relative URL, so it will
merge into the base URL of the client-- resulting in the derived URL of ``https://api.github.com/users``.

``/user`` is a relative URL but uses an absolute path because it contains the leading slash. Absolute paths will
overwrite any existing path of the base URL. If an absolute path is provided (e.g. ``/path/to/something``), then the
path specified in the base URL of the client will be replaced with the absolute path, and the query string provided
by the relative URL will replace the query string of the base URL.

Omitting the leading slash and using relative paths will add to the path of the base URL of the client. So using a
client base URL of ``https://api.twitter.com/v1.1`` and creating a GET request with ``statuses/user_timeline.json``
will result in a URL of ``https://api.twitter.com/v1.1/statuses/user_timeline.json``. If a relative path and a query
string are provided, then the relative path will be appended to the base URL path, and the query string provided will
be merged into the query string of the base URL.

If an absolute URL is provided (e.g. ``http://httpbin.org/ip``), then the request will completely use the absolute URL
as-is without merging in any of the URL parts specified in the base URL.

Configuration options
~~~~~~~~~~~~~~~~~~~~~

The second argument of the client's constructor is an array of configuration data. This can include URI template data
or special options that alter the client's behavior:

+-------------------------------+-------------------------------------------------------------------------------------+
| ``redirect.disable``          | Disable HTTP redirects for every request created by the client.                     |
+-------------------------------+-------------------------------------------------------------------------------------+
| ``curl.options``              | Associative array of cURL options to apply to every request created by the client.  |
|                               | if either the key or value of an entry in the array is a string, Guzzle will        |
|                               | attempt to find a matching defined cURL constant automatically (e.g.                |
|                               | "CURLOPT_PROXY" will be converted to the constant ``CURLOPT_PROXY``).               |
+-------------------------------+-------------------------------------------------------------------------------------+
| ``ssl.certificate_authority`` | Set to true to use the Guzzle bundled SSL certificate bundle (this is used by       |
|                               | default, or null to use the bundle on your system, a string pointing to a file to   |
|                               | use a specific certificate file, a string pointing to a directory to use multiple   |
|                               | certificates, or ``false`` to disable SSL validation (not recommended).             |
|                               |                                                                                     |
|                               | When using  Guzzle inside of a phar file, the bundled SSL certificate will be       |
|                               | extracted to your system's temp folder, and each time a client is created an MD5    |
|                               | check will be performed to ensure the integrity of the certificate.                 |
+-------------------------------+-------------------------------------------------------------------------------------+
| ``request.params``            | Associative array of parameters to apply to the parameter collection of every       |
|                               | request created by the client. Note: parameters are not query string parameters.    |
|                               | Parameters in this context are simply contextual pieces of data that can be used    |
|                               | with request collaborators.                                                         |
+-------------------------------+-------------------------------------------------------------------------------------+
| ``command.params``            | When using a ``Guzzle\Service\Client`` object, this is an associative array of      |
|                               | default options to set on each command created by the client.                       |
+-------------------------------+-------------------------------------------------------------------------------------+

Here's an example showing how to set various configuration options.

.. code-block:: php

    use Guzzle\Http\Client;

    // Create a client and pass in optional configuration information
    $client = new Client('https://api.twitter.com/{version}', array(
        'version'        => 'v1.1',
        'curl.options'   => array(CURLOPT_PROXY => 'tcp://localhost:80'),
        'request.params' => array('foo' => 'bar')
    ));

Creating requests with a client
-------------------------------

A Client object exposes several methods used to create Request objects:

* Create a custom HTTP request: ``$client->createRequest($method, $uri, array $headers, $body)``
* Create a GET request: ``$client->get($uri, array $headers, $body)``
* Create a HEAD request: ``$client->head($uri, array $headers, $body)``
* Create a DELETE request: ``$client->delete($uri, array $headers, $body)``
* Create a POST request: ``$client->post($uri, array $headers, $postBody)``
* Create a PUT request: ``$client->put($uri, array $headers, $body)``
* Create a PATCH request: ``$client->patch($uri, array $headers, $body)``

.. code-block:: php

    use Guzzle\Http\Client;

    $client = new Client('http://baseurl.com/api/v1');

    // Create a GET request using Relative to base URL
    // URL of the request: http://baseurl.com/api/v1/path?query=123&value=abc)
    $request = $client->get('path?query=123&value=abc');
    $response = $request->send();

    // Create HEAD request using a relative URL with an absolute path
    // URL of the request: http://baseurl.com/path?query=123&value=abc
    $request = $client->head('/path?query=123&value=abc');
    $response = $request->send();

    // Create a DELETE request using an absolute URL
    $request = $client->delete('http://www.example.com/path?query=123&value=abc');
    $response = $request->send();

    // Create a PUT request using the contents of a PHP stream as the body
    // Specify custom HTTP headers
    $request = $client->put('http://www.example.com/upload', array(
        'X-Header' => 'My Header'
    ), fopen('http://www.test.com/', 'r'));
    $response = $request->send();

    // Create a POST request and add the POST files manually
    $request = $client->post('http://localhost:8983/solr/update')
        ->addPostFiles(array('file' => '/path/to/documents.xml'));
    $response = $request->send();

    // Check if a resource supports the DELETE method
    $supportsDelete = $client->options('/path')->send()->isMethodAllowed('DELETE');
    $response = $request->send();

Client objects create Request objects using a request factory (``Guzzle\Http\Message\RequestFactoryInterface``).
You can inject a custom request factory into the Client using ``$client->setRequestFactory()``, but you can typically
rely on a Client's default request factory.

.. _uri-templates:

URI templates
~~~~~~~~~~~~~

The ``$uri`` passed to one of the client's request creational methods or the base URL of a client can utilize URI
templates. Guzzle supports the entire `URI templates RFC <http://tools.ietf.org/html/rfc6570>`_. URI templates add a
special syntax to URIs that replace template place holders with user defined variables.

Every request created by a Guzzle HTTP client passes through a URI template so that URI template expressions are
automatically expanded:

.. code-block:: php

    $client = new Guzzle\Http\Client('https://example.com/', array('a' => 'hi'));
    $request = $client->get('/{a}');

Because of URI template expansion, the URL of the above request will become ``https://example.com/hi``. Notice that
the template was expanded using configuration variables of the client. You can pass in custom URI template variables
by passing the URI of your request as an array where the first index of the array is the URI template and the second
index of the array are template variables that are merged into the client's configuration variables.

.. code-block:: php

    $request = $client->get(array('/test{?a,b}', array('b' => 'there'));

The URL for this request will become ``https://test.com?a=hi&b=there``. URI templates aren't limited to just simple
variable replacements;  URI templates can provide an enormous amount of flexibility when creating request URIs.

.. code-block:: php

    $request = $client->get(array('http://example.com{+path}{/segments}{?query,data*}', array(
        'path'     => '/foo/bar',
        'segments' => array('one', 'two'),
        'query'    => 'test',
        'data'     => array(
            'more' => 'value'
        )
    )));

The resulting URL would become ``http://example.com/foo/bar/one/two?query=test&more=value``.

By default, URI template expressions are enclosed in an opening and closing brace (e.g. ``{var}``). If you are working
with a web service that actually uses braces (e.g. Solr), then you can specify a custom regular expression to use to
match URI template expressions.

.. code-block:: php

    $client->getUriTemplate()->setRegex('/\<\$(.+)\>/');
    $client->get('/<$a>');

You can learn about all of the different features of URI templates by reading the
`URI templates RFC <http://tools.ietf.org/html/rfc6570>`_.

Sending requests
----------------

Requests can be sent by calling the ``send()`` method of a Request object, but you can also send requests using the
``send()`` method of a Client.

.. code-block:: php

    $request = $client->get('http://www.amazon.com');
    $response = $client->send($request);

Sending requests in parallel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Client's ``send()`` method accept a single ``Guzzle\Http\Message\RequestInterface`` object or an array of
RequestInterface objects. When an array is specified, the requests will be sent in parallel.

Sending many HTTP requests serially (one at a time) can cause an unnecessary delay in a script's execution. Each
request must complete before a subsequent request can be sent. By sending requests in parallel, a pool of HTTP
requests can complete at the speed of the slowest request in the pool, significantly reducing the amount of time
needed to execute multiple HTTP requests. Guzzle provides a wrapper for the curl_multi functions in PHP.

Here's an example of sending three requests in parallel using a client object:

.. code-block:: php

    use Guzzle\Common\Exception\MultiTransferException;

    try {
        $responses = $client->send(array(
            $client->get('http://www.google.com/'),
            $client->head('http://www.google.com/'),
            $client->get('https://www.github.com/')
        ));
    } catch (MultiTransferException $e) {

        echo "The following exceptions were encountered:\n";
        foreach ($e as $exception) {
            echo $exception->getMessage() . "\n";
        }

        echo "The following requests failed:\n";
        foreach ($e->getFailedRequests() as $request) {
            echo $request . "\n\n";
        }

        echo "The following requests succeeded:\n";
        foreach ($e->getSuccessfulRequests() as $request) {
            echo $request . "\n\n";
        }
    }

If the requests succeed, an array of ``Guzzle\Http\Message\Response`` objects are returned. A single request failure
will not cause the entire pool of requests to fail. Any exceptions thrown while transferring a pool of requests will
be aggregated into a ``Guzzle\Common\Exception\MultiTransferException`` exception.

Persistent HTTP connections
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Persistent HTTP connections are an extremely important aspect of the HTTP/1.1 protocol that is often overlooked by
PHP HTTP clients. Persistent connections allows data to be transferred between a client and server without the need
to reconnect each time a subsequent request is sent, providing a significant performance boost to applications that
need to send many HTTP requests to the same host.

Reusing the same client when sending requests to the same server will ensure that you are utilizing HTTP persistent
connections. All HTTP requests sent using the same client object will use the same cURL multi handle. cURL will
maintain a cache of persistent connections on a multi handle. More information about cURL's internal design and
persistent connection handling can be found at http://curl.haxx.se/dev/internals.html.

Clients will by default create their own ``Guzzle\Http\Curl\CurlMulti`` object for sending requests. You can inject a
custom CurlMulti object into a client to utilize a custom CurlMulti object (for example, using the same CurlMulti
object with every client) using ``$client->setCurlMulti()``.

Customizing a Client
--------------------

Default HTTP headers
~~~~~~~~~~~~~~~~~~~~

Use ``$client->setDefaultHeaders()`` if you need to send the same HTTP headers with every request created by a client.

.. code-block:: php

    $client = new Guzzle\Http\Client();

    // Always send the following headers with each request
    $client->setDefaultHeaders(array(
        'Accept-Encoding' => 'deflate',
        'Accept'          => 'application/json'
    ));

    // Get the list of default client headers
    var_export($client->getDefaultHeaders());

    $request = $client->get('http://httpbin.com');
    echo $request->getHeader('Accept');
    // >>> application/json
    echo $request->getHeader('Accept-Encoding');
    // >>> deflate

    // Send the request and get the response
    $response = $request->send();

Specifying an array of default headers on a client will cause every request created by the client to always include
the array of default headers.

Setting a custom User-Agent
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default Guzzle User-Agent header is ``Guzzle/<Guzzle_Version> curl/<curl_version> PHP/<PHP_VERSION>``. You can
customize the User-Agent header of a client by calling the ``setUserAgent()`` method of a Client object.

.. code-block:: php

    // Completely override the default User-Agent
    $client->setUserAgent('Test/123');

    // Prepend a string to the default User-Agent
    $client->setUserAgent('Test/123', true);

Plugins and events
------------------

Guzzle provides easy to use request plugins that add behavior to requests based on signal slot event notifications
powered by the
`Symfony2 Event Dispatcher component <http://symfony.com/doc/2.0/components/event_dispatcher/introduction.html>`_. Any
event listener or subscriber attached to a Client object will automatically be attached to each request created by the
client.

Using the same cookie session for each request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Attach a ``Guzzle\Plugin\Cookie\CookiePlugin`` to a client which will in turn add support for cookies to every request
created by a client, and each request will use the same cookie session:

.. code-block:: php

    use Guzzle\Plugin\Cookie\CookiePlugin;
    use Guzzle\Plugin\Cookie\CookieJar\ArrayCookieJar;

    // Create a new cookie plugin
    $cookiePlugin = new CookiePlugin(new ArrayCookieJar());

    // Add the cookie plugin to the client
    $client->addSubscriber($cookiePlugin);

.. _client-events:

Events emitted from a client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A ``Guzzle\Http\Client`` object emits the following events:

+------------------------------+--------------------------------------------+------------------------------------------+
| Event name                   | Description                                | Event data                               |
+==============================+============================================+==========================================+
| client.create_request        | Called when a client creates a request     | * client: The client                     |
|                              |                                            | * request: The created request           |
+------------------------------+--------------------------------------------+------------------------------------------+

.. code-block:: php

    use Guzzle\Common\Event;
    use Guzzle\Http\Client;

    $client = new Client();

    // Add a listener that will echo out requests as they are created
    $client->getEventDispatcher()->addListener('client.create_request', function (Event $e) {
        echo 'Client object: ' . spl_object_hash($e['client']) . "\n";
        echo "Request object: {$request}\n";
    });
