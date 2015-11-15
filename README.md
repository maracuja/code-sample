# Code Sample™
I've been asked by several potential employers to supply a code sample and since most of
my work is on client sites there's a limit to what I can show in my Github profile so I've
picked a small feature that demonstrates the use of an external service and some light queue
use. This was an app from one of our sites ballball, that facilitated the translation of
content via Smartling which is a human translation service.

The basic idea is that an editor would login to the CMS, create a copy of an English
article, set it's language and then mark it "ready for translation" before saving. A
django signal would listen for the save event and if conditions were met, send the
article to Smartling for translation. (signals.py and tasks.py)

A human translator would then pick up the article in their Smartling console, provide a
translation and that would go through their internal QA process. When the translation
passed QA the Smartling API would post back to us the translation via an endpoint we
created. (views.py and urls.py)

A class called SmartlingService then abstracted all the nitty gritty of packaging up the
objects and the communication between the two systems (services/Smartling.py)

The things I like about it are: -
* The use of signals and queues, we did as much as we could to keep the CMS responsive so
the user gets an instant response when they hit save. The CMS does all the API handling
in the background.
* Smartling was sending us some headers in it's responses that were causing an error in
the API package we were using, but luckily django let's you override that if you make your
own render class. So we did.
* Uses RabbitMq as the message server, ie I had to install Rabbit/Celery/etc to get it working
