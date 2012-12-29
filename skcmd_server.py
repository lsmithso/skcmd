#!/usr/bin/env python

"""
A dbus server that proxies  
Auto-connects incoming calls
Provides command to make outgoing calls

"""


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
        self.sk = sk.Skype()
        if not self.sk.Client.IsRunning:
            self.sk.Client.Start()

        
        self.sk.Attach()
        self.sk.OnCallStatus  = self.on_call
        print 'Attached as %s' % self.sk.CurrentUser.Handle

    def on_call(self, call, status):
        print 'Call from: %s %s' % (call._GetPartnerHandle(), status)

    def place_call(self, contact):
        self.sk.PlaceCall(contact)

    
class SkypeObject(dbus.service.Object):
    @dbus.service.method(I_NAME, in_signature = '', out_signature = '')
    def place_call(self, contact ):
        return self.skype.place_call(contact)
    
    @dbus.service.method(I_NAME, in_signature = '', out_signature = '')
    def exit(self):
        print 'exit on client command'
        sys.exit(0)
        
        


def main():
    main_loop = dbus.mainloop.glib.DBusGMainLoop(set_as_default = True)

    session_bus = dbus.SessionBus()
    name = dbus.service.BusName(S_NAME, session_bus)
    
    s = SkypeServer()
    object = SkypeObject(session_bus, '/SkypeObject')
    object.skype = s
    
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
