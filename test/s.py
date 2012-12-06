import sys, os, time

import Skype4Py as sk
s = sk.Skype()

s.Attach()
print 'Attached'

print s.CurrentUser.Handle

def on_call(call, status):
    print 'call', call, status
    print call._GetPartnerHandle()
    if status == 'RINGING':
        print 'answer'
        call.Answer()
        print 'answered'
    
s.OnCallStatus =on_call



# s.PlaceCall('echo123')

time.sleep(30)
sys.exit(0)
print 'Full Name: %s' % s.CurrentUser.FullName

print 'Skype Status: %s' % s.CurrentUser.OnlineStatus
print 'Country: %s' % s.CurrentUser.Country

print 'Bontacts'

for f in s.Friends:
    print 'handle:', f.Handle
    print 'Full Name: %s' % f.FullName
    print 'Skype Status: %s' % f.OnlineStatus
    print 'Country: %s' % f.Country


s.PlaceCall('echo123')

    
