AI Web
======

A framework for running AI programming challenges
-------------------------------------------------

Still under active development.

 - It should now work as a standalone server without passwordless SSH. If you want to run multiple workers on separate servers, passwordless SSH authentication is needed.

 - Compile the Isolate submodule and make sure the path is correct in config.py

 - Run all of the following in separate terminals:

   - $ ./manage.py runserver
   - $ ./manage.py webserver_backend
   - $ ./manage.py run_matchmaker
   - $ ./manage.py run_worker

   - You can run more workers by repeating the last command.

 - See the requirements of the Isolate submodule if you have trouble running games.

 - If running multiple servers, they should all have the project code at the same place in the directory structure, running under the same username.

 - The system is in early development. There will be bugs.

 - Code has been taken from Zeta, Epsilon, the TCP server and other places.


