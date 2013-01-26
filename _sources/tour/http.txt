===================
HTTP client for PHP
===================

.. highlight:: php

Guzzle gives PHP developers complete control over HTTP requests while utilizing HTTP/1.1 best practices.  Guzzle's HTTP functionality is a robust framework built on top of the `PHP libcurl bindings <http://www.php.net/curl>`_.

Using a Client object
---------------------

Requests can be created by using methods of the ``Guzzle\Http\Client`` object.  When instantiating a client object, you can pass an optional "base URL" and optional array of configuration options.  A base URL is the full URL of the server you are connecting to, and it can include query string parameters and a base path.

.. code-block:: php

    use Guzzle\Http\Client;

    $client = new Client('https://api.github.com');
    $request = $client->get('/user')->setAuth('user', 'pass');
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

Notice that the URI provided to the client's ``get()`` method is relative. Relative URIs will always merge into the base URL of the client. There are a few rules that control how the URIs are merged.

In the above example, we passed ``/user`` to the ``get()`` method of the client. This is a relative URI, so it will merge into the base URL of the client-- resulting in the derived URL of ``https://api.github.com/users``.

``/user`` is a relative URL but uses an absolute path because it contains the leading slash. Absolute paths will overwrite any existing path of the base URL. If an absolute path is provided (e.g. ``/path/to/something``), then the path specified in the base URL of the client will be replaced with the absolute path, and the query string provided will replace the query string of the base URL.

Omitting the leading slash and using relative paths will add to the path of the base URL of the client. So using a client base URL of ``https://api.twitter.com/v1.1`` and creating a GET request with ``statuses/user_timeline.json`` will result in a URL of ``https://api.twitter.com/v1.1/statuses/user_timeline.json``. If a relative path and a query string are provided, then the relative path will be appended to the base URL path, and the query string provided will be merged into the query string of the base URL.

If an absolute URL is provided (e.g. ``http://httpbin.org/ip``), then the request will completely use the absolute URL as-is without merging in any of the URL parts specified in the base URL.

Configuration options
~~~~~~~~~~~~~~~~~~~~~

The second argument of the client's constructor is an array of configuration data. This can include URI template data or special options that alter the client's behavior:

- ``curl.options``: Associative array of cURL options to apply to every request created by the client.
- ``ssl.certificate_authority``: Set to true to use the bundled SSL certificate bundle, ``system`` to use the bundle on your system, a string pointing to a file to use a specific certificate authority, a string pointing to a directory to use multiple certificates, or ``false`` to disable SSL validation.
- ``request.params``: Associative array of parameters to apply to the parameter collection of every request created by the client.

.. code-block:: php

    $client = new Client('https://api.twitter.com/{version}', array(
        'version' => 'v1.1',
        'curl.options' => array(CURLOPT_PROXY => 'tcp://localhost:80'),
        'ssl.certificate_authority' => 'system',
        'request.params' => array('foo' => 'bar')
    ));

Sending requests and using responses
------------------------------------

Requests
~~~~~~~~

Requests can be created from a client using method names that match the HTTP verb.  Guzzle supports the following HTTP methods: GET, HEAD, DELETE, PUT, POST, PATCH, and OPTIONS.  You can use any other custom HTTP method by calling ``$client->createRequest($methodName)``.

.. code-block:: php

    use Guzzle\Http\Client;

    $client = new Client('http://baseurl.com/api/v1');

    // Relative to base URL (http://baseurl.com/api/v1/path?query=123&value=abc)
    $request = $client->get('path?query=123&value=abc');

    // Overrides base URL's path (http://baseurl.com/path?query=123&value=abc)
    $request = $client->head('/path?query=123&value=abc');

    // Delete using an Absolute URL
    $request = $client->delete('http://www.example.com/path?query=123&value=abc');

    // Create a PUT request using the contents of a PHP stream as the body
    $request = $client->put('http://www.example.com/upload', array(
        'X-Header' => 'My Header'
    ), fopen('http://www.test.com/', 'r'));

    // Create a POST request and add the POST files manually
    $request = $client->post('http://localhost:8983/solr/update')
        ->addPostFiles(array('file' => '/path/to/documents.xml'));

    // Check if a resource supports the DELETE method
    $supportsDelete = $client->options('/path')->send()->isMethodAllowed('DELETE');

If you know exactly what HTTP message you want to send, you can create request objects from messages::

    use Guzzle\Http\Message\RequestFactory;

    $request = RequestFactory::fromMessage(
        "PUT / HTTP/1.1\r\n" .
        "Host: test.com:8081\r\n" .
        "Content-Type: text/plain\r\n" .
        "Transfer-Encoding: chunked\r\n\r\n" .
        "this is the body"
    );

Request objects are all about building an HTTP message.  Each part of an HTTP request message can be set individually using methods on the request object or set in bulk using the ``setUrl()`` method.  Here's the format of an HTTP request with each part of the request referencing the method used to change it::

    PUT(a) /path(b)?query=123(c) HTTP/1.1(d)
    X-Header(e): header
    Content-Length(e): 4

    data(f)

+-------------------------+---------------------------------------------------------------------------------+
| a. **Method**           | The request method can only be set when instantiating a request                 |
+-------------------------+---------------------------------------------------------------------------------+
| b. **Path**             | ``$request->setPath('/path');``                                                 |
+-------------------------+---------------------------------------------------------------------------------+
| c. **Query**            | ``$request->getQuery()->set('query', '123');``                                  |
+-------------------------+---------------------------------------------------------------------------------+
| d. **Protocol version** | ``$request->setProtocolVersion('1.1');``                                        |
+-------------------------+---------------------------------------------------------------------------------+
| e. **Header**           | ``$request->setHeader('X-Header', 'header');``                                  |
+-------------------------+---------------------------------------------------------------------------------+
| f. **Entity Body**      |  ``$request->setBody('data'); // Only available with PUT, POST, PATCH, DELETE`` |
+-------------------------+---------------------------------------------------------------------------------+

PUT
^^^

You can send PUT requests with raw entity bodies::

    $response = $client->put('http://httpbin.org/put', null, 'this is the body')->send();

POST
^^^^

Guzzle helps to make it extremely easy to send POST requests.  POST requests will be sent with an ``application/x-www-form-urlencoded`` Content-Type header if no files are being sent in the POST.  If files are specified in the POST, then the Content-Type header will become ``multipart/form-data``.  Here's how to create a multipart/form-data POST request containing files and fields::

    $request = $client->post('http://httpbin.org/post')
        ->addPostFields(array('custom_key' => 'value'))
        ->addPostFiles(array('file' => '/path/to/file.xml'));

This can be achieved more succinctly-- ``post()`` accepts three arguments: the URL, optional headers, and the post fields.  To send files in the POST request, prepend the ``@`` symbol to the array value (just like you would if you were using the PHP ``curl_setopt`` function)::

    $request = $client->post('http://www.example.com/upload', null, array(
        'custom_field' => 'my custom value',
        'file_field'   => '@/path/to/file.xml'
    ));

.. note::

    Remember to **always** sanitize user input when sending POST requests::

        // Prevent users from accessing sensitive files by sanitizing input
        $_POST = array('firstname' => '@/etc/passwd');
        $request = $client->post('http://www.example.com', null, array (
            'firstname' => str_replace('@', '', $_POST['firstname'])
        ));

You can send POST requests with raw entity bodies::

    $response = $client->post('http://httpbin.org/post', null, 'this is the body')->send();

Responses
~~~~~~~~~

Sending a request will return a ``Guzzle\Http\Message\Response`` object.  You can view the HTTP response message by casting the Response object to a string.  Casting the response to a string will return the entity body of the response as a string too, so this might be an expensive operation if the entity body is stored in a file or network stream.  If you only want to see the response headers, you can call ``getRawHeaders()``.

The Response object contains helper methods for retrieving common response headers.  These helper methods normalize the variations of HTTP response headers::

    $response->getContentMd5();
    $response->getEtag();
    $response->getCacheControl();
    $response->getHeader('Content-Length');
    // ... There are methods for every known response header

The entity body object of a response can be retrieved by calling ``$response->getBody()``. The response EntityBody can be cast to a string, or you can pass ``true`` to this method to retrieve the body as a string.

JSON Responses
^^^^^^^^^^^^^^

You can easily parse and use a JSON response as an array using the ``json()`` method of a response. This method will always return an array if the response is valid JSON or if the response body is empty. You will get an exception if you call this method and the response is not valid JSON::

    $data = $response->json();
    echo gettype($data);
    // >>> array

XML Responses
^^^^^^^^^^^^^

You can easily parse and use a XML response as SimpleXMLElement object using the ``xml()`` method of a response. This method will always return a SimpleXMLElement object if the response is valid XML or if the response body is empty. You will get an exception if you call this method and the response is not valid XML::

    $xml = $response->xml();
    echo $xml->foo;
    // >>> Bar!

Request and response headers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HTTP message headers are case insensitive, multiple occurrences of any header can be present in an HTTP message (whether it's valid or not), and some servers require specific casing of particular headers.  Because of this, request and response headers are stored in ``Guzzle\Http\Message\Header`` objects.  The Header object can be cast as a string, counted, or iterated to retrieve each value from the header.  Casting a Header object to a string will return all of the header values concatenated together using a glue string (typically ', ').  Let's take the following example to see what is returned::

    $request = new Request('GET', 'http://httpbin.com/cookies');
    // addHeader will set and append to any existing header values
    $request->addHeader('Foo', 'bar');
    $request->addHeader('foo', 'baz');
    // setHeader overwrites any existing values
    $request->setHeader('Test', '123');

    // Requests can be cast as a string
    echo $request->getHeader('Foo');
    // >>> bar, baz
    echo $request->getHeader('Test');
    // >>> "123"

    // You can count the number of headers of a particular case insensitive name
    echo count($request->getHeader('foO'));
    // >>> 2

    // You can iterate over Header objects
    foreach ($request->getHeader('foo') as $header) {
        echo $header;
    }

    // Missing headers return NULL
    var_export($request->getHeader('Missing'));
    // >>> null

    // You can see all of the different variations of a header by calling raw() on the Header
    var_export($request->getHeader('foo')->raw());

Redirects
~~~~~~~~~

By default, Guzzle will automatically follow redirects using the non-RFC compliant implementation used by most web browsers. This means that redirects for POST requests are followed by a GET request. You can force RFC compliance by enabling the strict mode on a request's parameter object::

    // Set per request
    $request = $client->post();
    $request->getParams()->set('redirect.strict', true);
    // Set globally on a client so that all requests use strict redirects
    $client->getConfig()->set('request.params', array('redirect.strict' => true));

By default, Guzzle will redirect up to 5 times before throwing a ``Guzzle\Http\Exception\TooManyRedirectsException``. You can raise or lower this value using the ``redirect.max`` parameter of a request object::

    $request->getParams()->set('redirect.max', 2);

You can get the full chain of request/response objects that were sent to complete an HTTP transaction using the ``getPreviousResponse()`` method of a response object.::

    $response = $request->send();

    do {
        echo "{$response}\n\n";
        $response = $response->getPreviousResponse();
    } while ($response);

You can disable redirects on a client by passing a configuration option in the client's constructor::

    $client = new Client(null, array('redirect.disable' => true));

You can also disable redirects per request::

    $request->getParams()->set('redirect.disable', true);

Redirects and non-repeatable streams
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are redirected when sending data from a non-repeatable stream and some of the data has been read off of the stream, then you will get a ``Guzzle\Http\Exception\CouldNotRewindStreamException``. You can get around this error by adding a custom rewind method to the entity body object being sent in the request::

    $request = $client->post('http://httpbin.com/redirect/2', null, fopen('http://httpbin.com/get', 'r'));
    // Add a custom function that can be used to rewind the stream (reopen in this example)
    $request->getBody()->setRewindFunction(function ($body) {
        $body->setStream(fopen('http://httpbin.com/get', 'r'));
        return true;
    );
    $response = $client->send();

Cookies
-------

Cookies can be modified and retrieved from a request using the following methods::

    $request->addCookie($name, $value);
    $request->removeCookie($name);
    $value = $request->getCookie($name);
    $valueArray = $request->getCookies();

Use the :doc:`cookie plugin </guide/plugins>` if you need to reuse cookies between requests.

Dealing with errors
~~~~~~~~~~~~~~~~~~~

Exceptions
^^^^^^^^^^

Requests that receive a 4xx or 5xx response will throw a ``Guzzle\Http\Exception\BadResponseException``.  More specifically, 4xx errors throw a ``Guzzle\Http\Exception\ClientErrorResponseException``, and 5xx errors throw a ``Guzzle\Http\Exception\ServerErrorResponseException``.  You can catch the specific exceptions or just catch the BadResponseException to deal with either type of error.  Here's an example of catching a generic BadResponseException::

    try {
        $response = $client->get('/not_found.xml')->send();
    } catch (Guzzle\Http\Exception\BadResponseException $e) {
        echo 'Uh oh! ' . $e->getMessage();
    }

Throwing an exception when a 4xx or 5xx response is encountered is the default behavior of Guzzle requests.  This behavior can be overridden by adding an event listener with a higher priority than -255 that stops event propagation.  You can subscribe to ``request.error`` to receive notifications any time an unsuccessful response is received.

You can change the response that will be associated with the request by calling ``setResponse()`` on the ``$event['request']`` object passed into your listener, or by changing the ``$event['response']`` value of the ``Guzzle\Common\Event`` object that is passed to your listener.  Transparently changing the response associated with a request by modifying the event allows you to retry failed requests without complicating the code that uses the client.  This might be useful for sending requests to a web service that has expiring auth tokens.  When a response shows that your token has expired, you can get a new token, retry the request with the new token, and return the successful response to the user.

Here's an example of retrying a request using updated authorization credentials when a 401 response is received, overriding the response of the original request with the new response, and still allowing the default exception behavior to be called when other non-200 response status codes are encountered::

    // Add custom error handling to any request created by this client
    $client->getEventDispatcher()->addListener('request.error', function(Event $event) {

        if ($event['response']->getStatusCode() == 401) {

            $newRequest = $event['request']->clone();
            $newRequest->setHeader('X-Auth-Header', MyApplication::getNewAuthToken());
            $newResponse = $newRequest->send();

            // Set the response object of the request without firing more events
            $event['response'] = $newResponse;

            // You can also change the response and fire the normal chain of
            // events by calling $event['request']->setResponse($newResponse);

            // Stop other events from firing when you override 401 responses
            $event->stopPropagation();
        }

    });

cURL errors
^^^^^^^^^^^

Connection problems and cURL specific errors can also occur when transferring requests using Guzzle.  When Guzzle encounters cURL specific errors while transferring a single request, a ``Guzzle\Http\Exception\CurlException`` is thrown with an informative error message and access to the cURL error message.

A ``Guzzle\Common\Exception\ExceptionCollection`` exception is thrown when a cURL specific error occurs while transferring multiple requests in parallel.  You can then iterate over all of the exceptions encountered during the transfer.

Entity Bodies
~~~~~~~~~~~~~

`Entity body <http://www.w3.org/Protocols/rfc2616/rfc2616-sec7.html>`_ is the term used for the body of an HTTP message.  The entity body of requests and responses is inherently a `PHP stream <http://php.net/manual/en/book.stream.php>`_ in Guzzle.  The body of the request can be either a string or a PHP stream which are converted into a ``Guzzle\Http\EntityBody`` object using its factory method.  When using a string, the entity body is stored in a `temp PHP stream <http://www.php.net/manual/en/wrappers.php.php>`_.  The use of temp PHP streams helps to protect your application from running out of memory when sending or receiving large entity bodies in your messages.  When more than 2MB of data is stored in a temp stream, it automatically stores the data on disk rather than in memory.

EntityBody objects provide a great deal of functionality: compression, decompression, calculate the Content-MD5, calculate the Content-Length (when the resource is repeatable), guessing the Content-Type, and more.  Guzzle doesn't need to load an entire entity body into a string when sending or retrieving data; entity bodies are streamed when being uploaded and downloaded.

Here's an example of gzip compressing a text file then sending the file to a URL::

    use Guzzle\Http\EntityBody;

    $body = EntityBody::factory(fopen('/path/to/file.txt', 'r'));
    $body->compress();
    $response = $client->put('http://localhost:8080/uploads', null, $body)->send();

The body of the request can be specified in the ``Client::put()`` or ``Client::post()``  method, or, you can specify the body of the request by calling the ``setBody()`` method of any ``Guzzle\Http\Message\EntityEnclosingRequestInterface`` object.

The entity body received from a response is stored in a temp stream by default.  If you need the entity body of a response to use a destination other than a temporary stream (e.g. FTP, HTTP, a specific file, an open stream), you can set the entity body object that will be used to hold the response body by calling ``setResponseBody()`` on any request object.

Send HTTP requests in parallel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sending many HTTP requests serially (one at a time) can cause an unnecessary delay in a script's execution. Each request must complete before a subsequent request can be sent. By sending requests in parallel, a pool of HTTP requests can complete at the speed of the slowest request in the pool, significantly reducing the amount of time needed to execute multiple HTTP requests. Guzzle provides a wrapper for the curl_multi functions in PHP.

You can pass a single request or an array of requests to a client's ``send()`` method.  Here's an example of sending three requests in parallel using a client object::

    use Guzzle\Common\Exception\ExceptionCollection;

    try {
        $responses = $client->send(array(
            $client->get('http://www.google.com/'),
            $client->head('http://www.google.com/'),
            $client->get('https://www.github.com/')
        ));
    } catch (ExceptionCollection $e) {
        echo "The following exceptions were encountered:\n";
        foreach ($e as $exception) {
            echo $exception->getMessage() . "\n";
        }
    }

A single request failure will not cause the entire pool of requests to fail.  Any exceptions thrown while transferring a pool of requests will be aggregated into a ``Guzzle\Common\Exception\ExceptionCollection`` exception.

Managed persistent HTTP connections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Persistent HTTP connections are an extremely important aspect of the HTTP/1.1 protocol that is often overlooked by PHP HTTP clients. Persistent connections allows data to be transferred between a client and server without the need to reconnect each time a subsequent request is sent, providing a significant performance boost to applications that need to send many HTTP requests to the same host.  Guzzle implicitly manages persistent connections for all requests.

All HTTP requests sent through Guzzle are sent using the same cURL multi handle.  cURL will maintain a cache of persistent connections on a multi handle.  As long as you do not override the default ``Guzzle\Http\Curl\CurlMulti`` object in your clients, you will benefit from application-wide persistent connections.  More information about cURL's internal design and persistent connection handling can be found at http://curl.haxx.se/dev/internals.html.

Low level cURL access
~~~~~~~~~~~~~~~~~~~~~

Most of the functionality implemented in the libcurl bindings has been simplified and abstracted by Guzzle. Developers who need access to `cURL specific functionality <http://www.php.net/curl_setopt>`_ that is not abstracted by Guzzle (e.g. proxies and some SSL options) can still add cURL handle specific behavior to Guzzle HTTP requests by modifying the cURL options collection of a request::

    $request->getCurlOptions()->set(CURLOPT_SSL_VERIFYHOST, true);

You can add cURL options to every request sent from your client by adding configuration options to the `curl.options` array.  Clients will automatically map cURL constants for keys and values to their correct PHP value.

.. code-block:: php

    $client = new Guzzle\Http\Client('https://example.com/', array(
        'curl.options' => array(
            CURLOPT_SSL_VERIFYHOST   => false,
            'CURLOPT_SSL_VERIFYPEER' => false,
            CURLOPT_PROXY            => 'proxy.mydomain.com:8080',
            'CURLOPT_PROXYTYPE'      => 'CURLPROXY_HTTP'
        )
    ));

If you are using :doc:`Service Descriptions </guide/service/service_descriptions>` then you can override the cURL options within the definition of an operation, for example:

.. code-block:: json

    {
        "operations": {
            "get_users": {
                "httpMethod": "GET",
                "uri": "/users",
                "curl.options": {
                    "CURLOPT_CONNECTTIMEOUT": "100"
                }
            }
        }
    }

You can blacklist cURL options and headers from ever being sent by cURL by adding a ``blacklist`` configuration option to the ``curl.options`` array of your client. The following example demonstrates how to blacklist the ``CURLOPT_ENCODING`` option from ever being set on a request and prevents cURL from ever sending an ``Accept`` header on any request.

.. code-block:: php

    $client = new Guzzle\Http\Client('https://example.com/', array(
        'curl.options' => array(
            'blacklist' => array(CURLOPT_ENCODING, 'header.Accept')
        )
    ));

Other special options that can be set in the ``curl.options`` array include:

- ``debug``: Adds verbose cURL output to a temp stream owned by the cURL handle object
- ``progress``: Instructs cURL to emit events when IO events occur. This allows you to be notified when bytes are transferred over the wire by subscribing to a request's ``curl.callback.read``, ``curl.callback.write``, and ``curl.callback.progress`` events.

URI templates
-------------

Guzzle supports the entire `URI templates RFC <http://tools.ietf.org/html/rfc6570>`_.  URI templates add a special syntax to URIs that replace template place holders with user defined variables.

Every request created by a Guzzle HTTP client passes through a URI template so that URI template expressions are automatically expanded::

    $client = new Guzzle\Http\Client('https://example.com/', array('a' => 'hi'));
    $request = $client->get('/{a}');

Because of URI template expansion, the URL of the above request will become ``https://example.com/hi``.  Notice that the template was expanded using configuration variables of the client.  You can pass in custom URI template variables by passing the URI of your request as an array where the first index of the array is the URI template and the second index of the array are template variables that are merged into the client's configuration variables::

    $request = $client->get(array('/test{?a,b}', array('b' => 'there'));

The URL for this request will become ``https://test.com?a=hi&b=there``.  URI templates aren't limited to just simple variable replacements;  URI templates can provide an enormous amount of flexibility when creating request URIs::

    $request = $client->get(array('http://example.com{+path}{/segments}{?query,data*}', array(
        'path'     => '/foo/bar',
        'segments' => array('one', 'two'),
        'query'    => 'test',
        'data'     => array(
            'more' => 'value'
        )
    )));

The resulting URL would become ``http://example.com/foo/bar/one/two?query=test&more=value``.

By default, URI template expressions are enclosed in an opening and closing brace (e.g. ``{var}``).  If you are working with a web service that actually uses braces (e.g. Solr), then you can specify a custom regular expression to use to match URI template expressions::

    $client->getUriTemplate()->setRegex('/\<\$(.+)\>/');
    $client->get('/<$a>');

You can learn about all of the different features of URI templates by reading the `URI template RFC <http://tools.ietf.org/html/draft-gregorio-uritemplate-08>`_.

Plugins for common HTTP request behavior
----------------------------------------

Guzzle provides easy to use request plugins that add behavior to requests based on signal slot event notifications.

View the plugin documentation here: :doc:`Guzzle Plugins </guide/plugins>`
