# skcmd.py0.0.4  - A command line interface to Skype
##Introduction

skcmd.py is a command line interface to Skype. It is implemented as a client/server  pair. It has no GUI components at all and is designed for ease of use by the VI. 

The server logs Skype status messages to stdout, and executes Skype
commands on behalf of the client. In particular it logs incomming calls, friend  status changes and authz requests.

The client is a command line program that sends Skype requests to the
server for execution .  It is asynchronous and does not block on
outgoing/incoming/ calls etc.

skcnd.py depends on a running Skype desktop, and the skype4py package.

## Install

You may need to apt-get install some prerequisites:

```
sudo apt-get install python-dev
sudo apt-get install python-gobject

  ```


Install skcmd:


```
  git clone http://github.com:/lsmithso/skcmd.git
  cd skcmd
  sudo python setup.py install
```

This should automatically install  Python package dependancies, including skype4py.


## Run

### Starting

Start the Skype desktop program as normal and sign in

Open a terminal window and startt the skcmd server:

 skcmd.py s

The Skype desktop will prompt for an authorization of this program the first time it is run. I needed sighted help for this step. 

When the server starts, it logs who you are signed in as, then a list
of all your contacts. It then blocks, waiting for client commands or
Skype status changes.   

### Client Commands

All client commands must be run from a separate terminal window.  The
normal Skype desktop continues to run, so you will hear the usual
ringing and contact status change sounds.


### Voice calls

To make a call, run the client call command, using the skype handle:

 s    kcmd.py call echo123  

All being well, This should initiate a call to the Skype call test service.  Look for Skype status messages in the server terminal window.


Inbound calls are logged by the server. To answer  a call run:

      skcmd.py answer

### Chatting

To send a chat message:

     skcmd.py chat handle [chat message to send]

Sends its arguments as a chat message to the Skype user with
handle. If no message argument is given, then stdin is read and sent
until an empty line or EOF is input. The later is useful for sending
special shell characters without quoting.

### Voicemails

Voicemails can be listed, played and deleted. You must enable your
voicemail inbox using the Skype GUI.

To list the contents of your voicemail inbox:

    skcmd.py vms

This lists each voicemail message as as an index number, the display
name/handle of the caller, call date/time/ duration. and voicemail
status. The index is a small integer used to refer to the voicemail in
other vm commands.

Play a voicemail with:

    skcmd.py vmplay idx

Where idx the index number of the message displayed by the vms command.

Stop the currently playing voicemail with:

    skcmd.py vmstop

Delete a voicemail with:

    skcmd.py vmdelete idx

The voicemail list is re-indexed after each message is deleted.

### Command List

The complete list of client commands are:


authz handle 0|1 - Authorize   the contact with handle.

contacts - Prints a list of all your contacts in the format  handle/display name/full name/status.

auto_answer 0|1 - Turns off/on autoanswer. Default is off.

hangup - Finish the current call.

exit - Terminate the  skcmd server.

answer - Answer the current inbound call.

call handle - Place an outbound call to the user with handle. Handle
is the Skype id printed in the 1st column of the 'contacts' command.

tone tones - send DTMF tones, ie for POTS conferencing.

add_contact  - Sends an authz requests to handle

search = Search for a Skype user

chat - chat to to the user with handle.

status  Set your status to DND, INVISIBLE  etc

   mood - set your mood message

  vms - List all voicemails,.

  vmplay idx - Play the voicemail with index number idx

  vmstop - Stop the currently playing voicemail

  vmdelete idx - Delete the voicemail with id idx

help - A breif help message.


## Skype status changes

The server logs some Skype status messages to stdout, and  signals them on D-Bus.

Status logged includes inbound/outbound call progress (in particular
inbound call ringing), contact authorization requests, contact status
changes (online, away etc) and chat messages.

These are plain text messages so a TTS should be able to announce them.

skcmd also signal D-Bus with these status messages. A simple skcmd.el is included that listens for this signal and announces it to emacspeak. 



## Disclaimer

This software comes with absolutely no warranty whatsoever, and comes
AS-IS.  Do what you want with itt. I take no responsibility whatsoever
for it.

* Changes
Add tone command.
concat call and tone args into spaceless string.




