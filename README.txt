* skcmd.py - A command line interface to Skype
** Introduction

skcmd.py is a command line interface to Skype. It is implemented as a client/server  pair. It has no GUI components at all and is designed for ease of use by the VI. 

The server logs Skype status messages to stdout, and executes Skype
commands on behalf of the client. In particular it logs incomming calls, friend  status changes and authz requests.

The client is a command line program that sends Skype requests to the
server for execution .  It is asynchronous and does not block on
outgoing/incoming/ calls etc.

The command set is limited to what I had an immediate need for.   This avoids bloat and makes the client easy to use, but the lack of a 'add new contact' and 'chat' commands is restrictive. 

skcnd.py depends on a running Skype desktop, and the skype4py package.

** Install

Install the Python skype4py package:

git clone git://github.com/awahlig/skype4py.git
cd skype4py
sudo python setup.py install

I've tested skcmd with version 1.0.35. Earlier versions are unusable due to a threading bug.

skcmd is not yet packaged, so must be run drom the source tarball you
got this README file from.

** Run

Start the Skype desktop program as normal and sign in

Open a terminal window and startt the skcmd server:

python skcmd.py s

The Skype desktop will prompt for an authorization of this program the first time it is run. I needed sighted help for this step. 

When the server starts, it logs who you are signed in as, then a list
of all your contacts. It then blocks, waiting for client commands or
Skype status changes.   All client commands must be run from a separate terminal window.


To make a call, run the client call command, using the skype handle:

python skcmd.py call echo123  

All being well, This should initiate a call to the Skype call test service.  Look for Skype status messages in the server terminal window.


Inbound calls are logged by the server. To answer  a call run:

python skcmd.py answer

Throughout this the normal Skype desktop continues to run, so you will
hear the usual ringing and contact status change sounds.

The complete list of client commands are:


authz handle 0|1 - Authorize   the contact with handle.

contacts - Prints a list of all your contacts in the format  handle/display name/full name/status.

auto_answer 0|1 - Turns off/on autoanswer. Default is off.

hangup - Finish the current call.

exit - Terminate the  skcmd server.

answer - Answer the current inbound call.

call handle - Place an outbound call to the user with handle. Handle
is the Skype id printed in the 1st column of the 'contacts' command.

help - A breif help message.


** Skype status changes

The server logs some Skype status messages to stdout, and  signals them on D-Bus.

Status logged includes inbound/outbound call progress (in particular inbound call ringing), contact authorization  requests and contact status changes (online, away etc).

These are plain text messages so a TTS should be able to announce them.

skcmd also signal D-Bus with these status messages. A simple skcmd.el is included that listens for this signal and announces it to emacspeak. 


** TODO

Packaging
Upload to some code repo somwhere
More commands -  add new contact and chat.
Better byilt in help command.
More d-bus clients - e.g., one that announces incoming calls to espeak.
Licencing model.


** Disclaimer

This software comes with absolutely no warranty whatsoever, and comes
AS-IS.  Do what you want with itt. I take no responsibility whatsoever
for it.



