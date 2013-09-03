#!/usr/bin/env python



import sys, datetime, os
import gobject
import dbus
import dbus.service
import dbus.mainloop.glib
import glib
import logging
import Skype4Py as sk

if os.getenv('SKCMD_DEBUG'):
    logging.basicConfig(level=logging.DEBUG)                                                      


I_NAME = "uk.co.opennet.skypecmd_interface"
S_NAME = "uk.co.opennet.skypecmd_service"

def timestamp():
    n = datetime.datetime.now()
    return n.strftime('%H:%M')

class SkypeServer(object):
    def __init__(self):
	self.auto_answer = False
        self.state = None
        self.call = None
	self.vm_id = None
	
        self.sk = sk.Skype(RunMainLoop = False)
	self.sk.Timeout = 60000
        if not self.sk.Client.IsRunning:
            self.sk.Client.Start()

        
        self.sk.Attach()
        self.sk.OnCallStatus  = self.on_call
	self.sk.OnOnlineStatus = self.on_online_status
	self.sk.OnUserAuthorizationRequestReceived = self.on_authz
	self.sk.OnMessageStatus = self.on_message
	self.sk.OnAsyncSearchUsersFinished = self.on_search_finished
	self.sk.OnUserMood = self.on_user_mood


	
        print timestamp(), 'Attached as %s - %s. Balance: %s vm: %d missed: %d' % (self.sk.CurrentUser.Handle, self.sk.CurrentUser.FullName, self.sk.CurrentUserProfile.BalanceToText, len(self.sk.Voicemails), len(self.sk.MissedVoicemails))
	for f in self.sk.Friends:
	    print self.user_names(f)
	sys.stdout.flush()

    def user_names(self, u):
	rv = '%s/%s/%s/%s' % (u.Handle, u.DisplayName, u.FullName, u.OnlineStatus, )
	if u.IsVoicemailCapable:
	    rv += '/vm'
	return rv

    def on_user_mood(self, user, mood):
	print '%s User %s mood %s' % (timestamp(), self.user_names(user), mood)
	sys.stdout.flush()
	self.signal_call_status(user.Handle, mood)
		
    def on_search_finished(self, sid, users):
	l = len(users)
	for i, user in enumerate(users):
	    print '%s Found %d/%d: %s' % (timestamp(), i + 1, l, self.user_names(user)) 
	sys.stdout.flush()
	    

    def on_message(self, chat, status):
	if status in ('RECEIVED','SENDING'):
	    print timestamp(), status, chat.FromHandle, chat.Body
	    sys.stdout.flush()
	if  status == 'RECEIVED':
	    	self.signal_call_status(chat.FromHandle, chat.Body)
		
	    	chat.MarkAsSeen()

	
	

    def on_authz(self, user):
	print '%s-Authz request from: %s' % (timestamp(), self.user_names(user))
	self.signal_call_status(self.user_names(user), 'authz request')
	sys.stdout.flush()


	
    def on_online_status(self, user, status):
	print '%s-%s - %s' % (timestamp(), status, self.user_names(user))
	sys.stdout.flush()
		
	self.signal_call_status(self.user_names(user), status)


    def on_call(self, call, status):
        self.call = call
        partner_id = call._GetPartnerHandle()
	user = self.sk.User(partner_id)
        print '%s-Call : %s %s' % (timestamp(), self.user_names(user), status)
	sys.stdout.flush()
        self.signal_call_status(self.user_names(user), status)
        if status in ('FINISHED', 'CANCELLED'):
            self.state = None
            self.call = None
        elif status == 'RINGING' and not self.state and self.auto_answer:
            print 'answering'
            call.Answer()


    def place_call(self, contact):
        self.sk.PlaceCall(contact)
        self.state = 'call placed'

	

    def tone(self, v):
        if self.call:
	    for t in v:
		if t in '0123456789#*':
		    self.call.DTMF = t
	    
    def finish(self):
        if self.call:
            self.call.Finish()

    def set_auto_answer(self, on):
	self.auto_answer = True if on in ('1', 'y', 'Y') else False
	return str(self.auto_answer)

    def answer(self):
	if self.call and not self.state and not self.auto_answer:
	    self.call.Answer()
	
    def contacts(self):
	return [self.user_names(x) for x in  self.sk.Friends]
    
    def authz(self, name, status):
	user = self.sk.User(name)
	user.IsAuthorized = True if status == '1' else False

    def add_contact(self, name, msg):
	if not msg:
	    msg = 'Can I add you as a friend?'
	user = self.sk.User(name)
	user.SetBuddyStatusPendingAuthorization(msg)

    def chat(self, user, msg):
	c = self.sk.CreateChatWith(user)
	c.SendMessage(msg)

    def search(self, name):
	self.sk.AsyncSearchUsers(name)

    def change_status(self, status):
	self.sk.CurrentUserStatus = status.upper()

    def change_mood(self, mood):
	self.sk.CurrentUserProfile.MoodText = mood

    def vm_play(self, vm_id):
	self.vm_id = vm_id
	vm = self.sk.Voicemail(vm_id)
	if self.call:
	    vm.StartPlaybackInCall()
	else:
	    vm.StartPlayback()
	


    def vm_stop_playback(self):
	vm = self.sk.Voicemail(self.vm_id)
	vm.StopPlayback()
	


    def vm_delete(self, vm_id):
	vm = self.sk.Voicemail(vm_id)
	vm.Delete()

	    
    
class SkypeObject(dbus.service.Object):
    @dbus.service.method(I_NAME, in_signature = '', out_signature = '')
    def call(self, contact ):
        return self.skype.place_call(contact)


    @dbus.service.method(I_NAME, in_signature = '', out_signature = '')
    def hangup(self):
        self.skype.finish()


    @dbus.service.method(I_NAME, in_signature = 's', out_signature = '')
    def tone(self, v):
        self.skype.tone(v)

    @dbus.service.signal(dbus_interface = I_NAME, signature='ss')
    def signal_call_status(self, caller_id, status):
        pass

    
    @dbus.service.method(I_NAME, in_signature = '', out_signature = '')
    def exit(self):
        print timestamp(), 'exit on client command'
        sys.exit(0)
        
    @dbus.service.method(I_NAME, in_signature = 's', out_signature = 's')
    def auto_answer(self, on):
        return self.skype .set_auto_answer(on)
    
    @dbus.service.method(I_NAME, in_signature = '', out_signature = '')
    def answer(self):
	self.skype .answer()
	
    @dbus.service.method(I_NAME, in_signature = '', out_signature = 'as')
    def contacts(self):
	return self.skype .contacts()

    @dbus.service.method(I_NAME, in_signature = 'ss', out_signature = '')
    def authz(self, user, status):
	self.skype.authz(user, status)

    @dbus.service.method(I_NAME, in_signature = 's', out_signature = '')
    def add_contact(self, user):
	self.skype.add_contact(user, msg = None)
	

    @dbus.service.method(I_NAME, in_signature = 'ss', out_signature = '')
    def chat(self, user, msg):
	self.skype.chat(user, msg)

    @dbus.service.method(I_NAME, in_signature = 's', out_signature = '')
    def search(self, name):
	self.skype.search(name)

    @dbus.service.method(I_NAME, in_signature = 's', out_signature = '')
    def status(self, st):
	self.skype.change_status(st)

    @dbus.service.method(I_NAME, in_signature = 's', out_signature = '')
    def mood(self, mood_text):
	self.skype.change_mood(mood_text)

    @dbus.service.method(I_NAME, in_signature = 'i', out_signature = '')
    def vmplay(self, vm_id):
	self.skype.vm_play(vm_id)

    @dbus.service.method(I_NAME, in_signature = '', out_signature = '')
    def vmstop(self):
	self.skype.vm_stop_playback()


    @dbus.service.method(I_NAME, in_signature = 'i', out_signature = '')
    def vmdelete(self, vm_id):
	self.skype.vm_delete(vm_id)

def main():
    mainloop1 = dbus.mainloop.glib.DBusGMainLoop(set_as_default = True)

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

    def command_list(self):
	return [x  for x in SkypeObject.__dict__ if x[0] != '_']

	


class ClientVM(object):
    # Listing voicemails in the server hangs but all other vm ops work
    # fine. The workaround is to attach to skype in the client to get
    # the vm list and to map vm ids to a small integer. When making
    # server voicemail calls (ie play), the small integer is mapped to
    # a voicemail id, which the server then maps to a voicemail
    # object.
    
    def  __init__(self):
	self.skc = sk.Skype()
	self.skc.Attach()

    def idx_2_id(self, idx):
	vms = self.skc.Voicemails
	return vms[idx].Id
	    
    def print_vms(self):
	vms = self.skc.Voicemails
	for i, vm in enumerate(vms):
	    print '%d: %s/%s %s/%s %s' % (i, vm.PartnerDisplayName, vm.PartnerHandle, vm.Datetime,vm.Duration, vm.Status)
	    
    
if __name__ == '__main__':
    if sys.argv[1] == 's':
        main()
	sys.exit(0)
    if sys.argv[1].startswith('vm'):
	vmc = ClientVM()
    if sys.argv[1] == 'vms':
	vmc.print_vms()
    else:
        c = SkypeClient()
	if sys.argv[1] == 'contacts':
	    print '\n'.join(c.command(*sys.argv[1:]))
	elif sys.argv[1] == 'chat':
	    if len(sys.argv) == 3:
		# No chat message on cmd line
		while True:
		    l = raw_input('? ')
		    if not l:
			break
		    c.command(sys.argv[1], sys.argv[2], l)
	    else:
		c.command(sys.argv[1], sys.argv[2], ' '.join(sys.argv[3:]))
	elif sys.argv[1] == 'mood':
	    c.command(sys.argv[1], ' '.join(sys.argv[2:]))
	elif sys.argv[1] in ('call', 'tone'):
	    c.command(sys.argv[1], ''.join(sys.argv[2:]))
	elif  sys.argv[1] in ('vmplay', 'vmdelete'):
	    vm_id = vmc.idx_2_id(int(sys.argv[2]))
	    c.command(sys.argv[1], vm_id)
	elif sys.argv[1] =='help':
	    print '\n'.join(c.command_list())
	else:
	    rsp =  c.command(*sys.argv[1:])
	    if rsp:
		print rsp


