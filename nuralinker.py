import os
import json

from django.shortcuts import redirect

from .user import Session
from.user import User

from django.http import HttpResponseForbidden
from django.http import HttpResponse

path = 'Nurallinker/'
path_users = path + 'users.json'
path_linkers = path + 'linkers/'

linkers = {}

f_accounts = open(path_users, 'r')  # ro
data = json.load(f_accounts)
f_accounts.close()

users = data['users']
sessions = data['sessions']

for uname in users:
    lks = users[uname]['linkers']
    for lname in lks:
        lkr = lks[lname]
        lp = lkr['resource']
        linkers[lp] = lkr


def save():
    f_accounts = open(path_users, 'w')  # wo
    json.dump(data, f_accounts)
    f_accounts.close()


# csrf protection and account getter

def auth(request):
    save()
    cookies = request.COOKIES
    if request.method == 'POST':
        if 'sestok' not in cookies:
            return False, HttpResponseForbidden('Form submitted with no session cookie')
        if 'sestok' not in request.POST:
            return False, HttpResponseForbidden('Form submitted with no session field')
        if not cookies['sestok'] == request.POST['sestok']:
            return False, HttpResponseForbidden('Form session field does not match session cookie, csrf?')
    
    if 'sestok' in cookies:
        sestok = cookies['sestok']
    else:
        sestok = ''

    if sestok not in sessions:  # new session, the browser does not yet have one
        sess = Session['new']()  # gen a session
        sessions[sess['token']] = sess  # save the session
        return True, sess

    # browser has a session
    return True, sessions[sestok]

    #returns the user object and raises the Http403 error for a csrf attempt


