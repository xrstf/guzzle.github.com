==============================
Creating Plugins and Observers
==============================

.. highlight:: php

Guzzle is extremely extendable because of the behavioral modifications that can be added to requests, clients, and
commands using an event system. Before and after the majority of actions are taken in the library, an event is emitted
with the name of the event and context surrounding the event. Observers can subscribe to a subject and modify the
subject based on the events received. Guzzle's event system utilizes the Symfony2 EventDispatcher and is the backbone
of it's plugin architecture.

Overview
--------

Plugins must implement the ``Symfony\Component\EventDispatcher\EventSubscriberInterface`` interface. The
``EventSubscriberInterface`` requires that your class implements a static method, ``getSubscribedEvents()``, that
returns an associative array mapping events to methods on the object. See the
`Symfony2 documentation <http://symfony.com/doc/2.0/book/internals.html#the-event-dispatcher>`_ for more information.

Plugins can be attached to any subject, or object in Guzzle that implements that
``Guzzle\Common\HasDispatcherInterface``.

Subscribing to a subject
~~~~~~~~~~~~~~~~~~~~~~~~

You can subscribe an instantiated observer to an event by calling ``addSubscriber`` on a subject.

.. code-block:: php

    $testPlugin = new TestPlugin();
    $client->addSubscriber($testPlugin);

You can also subscribe to only specific events using a closure::

    $client->getEventDispatcher()->addListener('request.create', function(Event $event) {
        echo $event->getName();
        echo $event['request'];
    });

``Guzzle\Common\Event`` objects are passed to notified functions.  The Event object has a ``getName()`` method which
return the name of the emitted event and may contain contextual information that can be accessed like an array.

Knowing what events to listen to
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any class that implements the ``Guzzle\Common\HasDispatcherInterface`` must implement a static method,
``getAllEvents()``, that returns an array of the events that are emitted from the object.  You can browse the source
to see each event, or you can call the static method directly in your code to get a list of available events.

Event hooks
-----------

+---------------------------------+-----------------------------+----------------------------------+-------------------------------------+
| Subject                         | Event                       | Description                      | Arguments                           |
+=================================+=============================+==================================+=====================================+
| ``Guzzle\Http\Client``          | client.create_request       | Client has created a request     | * client: The client                |
|                                 |                             |                                  | * request: The created request      |
+---------------------------------+-----------------------------+----------------------------------+-------------------------------------+
| ``Guzzle\Http\Message\Request`` | request.before_send         | About to send request            | * request: Request to be sent       |
|                                 +-----------------------------+----------------------------------+-------------------------------------+
|                                 | request.sent                | Sent the request                 | * request: Request that was sent    |
|                                 |                             |                                  | * response: Received response       |
|                                 +-----------------------------+----------------------------------+-------------------------------------+
|                                 | request.complete            | Completed a full HTTP transaction| * request: Request that was sent    |
|                                 |                             |                                  | * response: Received response       |
|                                 +-----------------------------+----------------------------------+-------------------------------------+
|                                 | request.success             | Completed a successful request   | * request: Request that was sent    |
|                                 |                             |                                  | * response: Received response       |
|                                 +-----------------------------+----------------------------------+-------------------------------------+
|                                 | request.error               | Completed an unsuccessful request| * request: Request that was sent    |
|                                 |                             |                                  | * response: Received response       |
|                                 +-----------------------------+----------------------------------+-------------------------------------+
|                                 | request.exception           | An unsuccessful response was     | * request: Request                  |
|                                 |                             | received.                        | * response: Received response       |
|                                 |                             |                                  | * exception: BadResponseException   |
|                                 +-----------------------------+----------------------------------+-------------------------------------+
|                                 | request.receive.status_line | Received the start of a response | * line: Full response start line    |
|                                 |                             |                                  | * status_code: Status code          |
|                                 |                             |                                  | * reason_phrase: Reason phrase      |
|                                 |                             |                                  | * previous_response: (e.g. redirect)|
|                                 +-----------------------------+----------------------------------+-------------------------------------+
|                                 | request.set_response        | A response was set on the request| * request: Request                  |
|                                 |                             |                                  | * response: Response that was set   |
|                                 +-----------------------------+----------------------------------+-------------------------------------+
|                                 | curl.callback.progress      | cURL progress event (only        | * request: Request                  |
|                                 |                             | dispatched when emit_io is       | * handle: CurlHandle                |
|                                 |                             | set on a request's curl options  | * download_size: Total download size|
|                                 |                             |                                  | * downloaded: Bytes downloaded      |
|                                 |                             |                                  | * upload_size: Total upload bytes   |
|                                 |                             |                                  | * uploaded: Bytes uploaded          |
|                                 +-----------------------------+----------------------------------+-------------------------------------+
|                                 | curl.callback.write         | cURL event called when data is   | * request: Request                  |
|                                 |                             | written to an outgoing stream    | * write: Data being written         |
|                                 +-----------------------------+----------------------------------+-------------------------------------+
|                                 | curl.callback.read          | cURL event called when data is   | * request: Request                  |
|                                 |                             | written to an incoming stream    | * read: Data being read             |
+---------------------------------+-----------------------------+----------------------------------+-------------------------------------+
| ``Guzzle\Http\Curl\CurlMulti``  | curl_multi.add_request      | Added a request                  | * request: Request being added      |
|                                 +-----------------------------+----------------------------------+-------------------------------------+
|                                 | curl_multi.remove_request   | Removed a request                | * request: Request being removed    |
|                                 +-----------------------------+----------------------------------+-------------------------------------+
|                                 | curl_multi.before_send      | About to send handles            | * requests: Array of Request objects|
|                                 +-----------------------------+----------------------------------+-------------------------------------+
|                                 | curl_multi.polling_request  | Polling a specific handle        | * request: Request being polled     |
|                                 |                             |                                  | * curl_multi: cURL multi handle     |
|                                 +-----------------------------+----------------------------------+-------------------------------------+
|                                 | curl_multi.complete         | Completed a multi transfer       |                                     |
|                                 +-----------------------------+----------------------------------+-------------------------------------+
|                                 | curl_multi.exception        | Encountered an exception during  | * exception: Exception encountered  |
|                                 |                             | the transfer                     | * all_exceptions: All buffered      |
|                                 |                             |                                  |   exception                         |
+---------------------------------+-----------------------------+----------------------------------+-------------------------------------+
| ``Guzzle\Service\Client``       | client.command.create       | Client has created a command     | * client: The client                |
|                                 |                             |                                  | * command: The created command      |
|                                 +-----------------------------+----------------------------------+-------------------------------------+
|                                 | command.before_prepare      | Before a command is prepared     | * command: Command being prepared   |
|                                 +-----------------------------+----------------------------------+-------------------------------------+
|                                 | command.before_send         | Before a command is executed     | * command: Command about to send    |
|                                 +-----------------------------+----------------------------------+-------------------------------------+
|                                 | command.after_send          | After a command is executed      | * command: Command that was sent    |
|                                 +-----------------------------+----------------------------------+-------------------------------------+
|                                 | command.after_send          | After a command is executed      | * command: Command that was sent    |
+---------------------------------+-----------------------------+----------------------------------+-------------------------------------+

Examples of the event system
----------------------------

Simple Echo plugin
~~~~~~~~~~~~~~~~~~

This simple plugin echos a string containing the request that is about to be sent by listening to the
``request.before_send`` event::

    class EchoPlugin implements Symfony\Component\EventDispatcher\EventSubscriberInterface
    {
        public static function getSubscribedEvents()
        {
            return array(
                'request.before_send' => 'onBeforeSend'
            );
        }

        public function onBeforeSend(Guzzle\Common\Event $event)
        {
            echo 'About to send a request: ' . $event['request'] . "\n";
        }
    }

    $plugin = new EchoPlugin();
    $client = new Guzzle\Service\Client('http://www.test.com/');
    $client->addSubscriber($plugin);
    $client->get('/')->send();


Running the above code will echo a string containing the HTTP request that is about to be sent.
