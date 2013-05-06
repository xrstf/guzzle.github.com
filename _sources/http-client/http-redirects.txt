==============
HTTP redirects
==============

By default, Guzzle will automatically follow redirects using the non-RFC compliant implementation used by most web
browsers. This means that redirects for POST requests are followed by a GET request. You can force RFC compliance by
enabling the strict mode on a request's parameter object:

.. code-block:: php

    // Set per request
    $request = $client->post();
    $request->getParams()->set('redirect.strict', true);
    // Set globally on a client so that all requests use strict redirects
    $client->getConfig()->set('request.params', array('redirect.strict' => true));

By default, Guzzle will redirect up to 5 times before throwing a ``Guzzle\Http\Exception\TooManyRedirectsException``.
You can raise or lower this value using the ``redirect.max`` parameter of a request object:

.. code-block:: php

    $request->getParams()->set('redirect.max', 2);

Redirect history
----------------

You can get the full chain of request/response objects that were sent to complete an HTTP transaction using the
``getPreviousResponse()`` method of a response object.

.. code-block:: php

    $response = $request->send();

    do {
        echo "{$response}\n\n";
        $response = $response->getPreviousResponse();
    } while ($response);

Disabling redirects
-------------------

You can disable redirects on a client by passing a configuration option in the client's constructor:

.. code-block:: php

    $client = new Client(null, array('redirect.disable' => true));

You can also disable redirects per request:

.. code-block:: php

    $request->getParams()->set('redirect.disable', true);

Redirects and non-repeatable streams
------------------------------------

If you are redirected when sending data from a non-repeatable stream and some of the data has been read off of the
stream, then you will get a ``Guzzle\Http\Exception\CouldNotRewindStreamException``. You can get around this error by
adding a custom rewind method to the entity body object being sent in the request.

.. code-block:: php

    $request = $client->post('http://httpbin.com/redirect/2', null, fopen('http://httpbin.com/get', 'r'));
    // Add a custom function that can be used to rewind the stream (reopen in this example)
    $request->getBody()->setRewindFunction(function ($body) {
        $body->setStream(fopen('http://httpbin.com/get', 'r'));
        return true;
    );
    $response = $client->send();
