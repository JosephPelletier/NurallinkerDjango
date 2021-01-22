import secrets
import hashlib


def nuser(uname, auhash=''):
    return {'auhash': auhash, 'uname': uname, 'sess': {}, 'linkers': {}}


def uhash(self, passwd):
    hg = hashlib.sha256()
    hg.update(self['uname'].encode('utf-8'))
    hg.update('/'.encode('utf-8'))  # no two users have the same passwd hash because '/' is not legal in usernames
    hg.update(passwd.encode('utf-8'))
    return hg.hexdigest()


def auth(self, passwd):
    return self['auhash'] == uhash(self, passwd)


def setpasswd(self, passwd):
    self['auhash'] = uhash(self, passwd)


User = {'new': nuser, 'uhash': uhash, 'auth': auth, 'setpasswd': setpasswd}

def nsession(token = secrets.token_bytes(32).hex(), uname = ''):
    return {'token': token, 'uname': uname}


Session = {'new': nsession}

