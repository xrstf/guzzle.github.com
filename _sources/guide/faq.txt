===
FAQ
===

What should I do if I get this error: Fatal error: Maximum function nesting level of '100' reached, aborting!
-------------------------------------------------------------------------------------------------------------

You could run into this error if you have the XDebug extension installed and you execute a lot of requests in callbacks.  This error message comes specifically from the XDebug extension. PHP itself does not have a function nesting limit. Change this setting in your php.ini to increase the limit:

xdebug.max_nesting_level = 1000

[`source <http://stackoverflow.com/a/4293870/151504>`_]

How can I speed up my client?
-----------------------------

There are several things you can do to speed up your client:

1. Disable type validation on your ``Guzzle\Service\Inspector``
2. Utilize a C based HTTP message parser (e.g. ``Guzzle\Http\Parser\Message\PeclHttpMessageParser``)

Why am I getting a 417 error response?
--------------------------------------

This can occur for a number of reasons, but if you are sending PUT, POST, or PATCH requests with an ``Expect: 100-Continue`` header, a server that does not support this header will return a 417 response. You can work around this by calling ``$request->removeHeader('Expect');`` after setting the entity body of a request.
