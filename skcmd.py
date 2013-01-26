#!/usr/bin/env python

"""
A dbus server that proxies  
Auto-connects incoming calls
Provides command to make outgoing calls

"""

# TODO:
# List online contacts
# announce contact status change?
# Delay before auto-answering
# auto accept new contacts

import sys
import gobject
import dbus
import dbus.service
import dbus.mainloop.glib
import glib
import Skype4Py as sk

I_NAME = "uk.co.opennet.skypecmd_interface"
S_NAME = "uk.co.opennet.skypecmd_service"


class SkypeServer(object):
    def __init__(self):
	self.auto_answer = False
        self.state = None
        self.call = None
        self.sk = sk.Skype()
        if not self.sk.Client.IsRunning:
            self.sk.Client.Start()

        
        self.sk.Attach()
        self.sk.OnCallStatus  = self.on_call
        print 'Attached as %s' % self.sk.CurrentUser.Handle

    def on_call(self, call, status):
        self.call = call
        caller_id = call._GetPartnerHandle()
        print 'Call from: %s %s state: %r' % (caller_id, status, self.state)
        self.signal_call_status(caller_id, status)
                    
        if status in ('FINISHED', 'CANCELLED'):
            self.state = None
            self.call = None
        elif status == 'RINGING' and not self.state and self.auto_answer:
            print 'answering'
            call.Answer()

            

    def place_call(self, contact):
        self.sk.PlaceCall(contact)
        self.state = 'call placed'

    def finish(self):
        if self.call:
            self.call.Finish()

    def set_auto_answer(self, on):
	self.auto_answer = True if on in ('1', 'y', 'Y') else False
	return str(self.auto_answer)

    def answer(self):
	if self.call and not self.state and not self.auto_answer:
	    self.call.Answer()
	
	

    
class SkypeObject(dbus.service.Object):
    @dbus.service.method(I_NAME, in_signature = '', out_signature = '')
    def call(self, contact ):
        return self.skype.place_call(contact)

    @dbus.service.method(I_NAME, in_signature = '', out_signature = '')
    def hangup(self):
        self.skype.finish()
    
    @dbus.service.signal(dbus_interface = I_NAME, signature='ss')
    def signal_call_status(self, caller_id, status):
        pass

    
    @dbus.service.method(I_NAME, in_signature = '', out_signature = '')
    def exit(self):
        print 'exit on client command'
        sys.exit(0)
        
    @dbus.service.method(I_NAME, in_signature = 's', out_signature = 's')
    def auto_answer(self, on):
        return self.skype .set_auto_answer(on)
    
    @dbus.service.method(I_NAME, in_signature = '', out_signature = '')
    def answer(self):
	self.skype .answer()

    


def main():
    main_loop = dbus.mainloop.glib.DBusGMainLoop(set_as_default = True)

    session_bus = dbus.SessionBus()
    name = dbus.service.BusName(S_NAME, session_bus)
    
    s = SkypeServer()
    object = SkypeObject(session_bus, '/SkypeObject')
    object.skype = s
    s.signal_call_status = object.signal_call_status
    
    mainloop = gobject.MainLoop()
    mainloop.run()
    

class SkypeClient(object):
    def __init__(self):
        self.bus = dbus.SessionBus()
        self.remote_object = self.bus.get_object(S_NAME, '/SkypeObject')

    def command(self, cmd, *args):
        return getattr(self.remote_object, cmd)(*args)
    
if __name__ == '__main__':
    if sys.argv[1] == 's':
        main()    
    else:
        c = SkypeClient()
        print c.command(*sys.argv[2:])
