from django.shortcuts import render

# Create your views here.
import urllib
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from .nuralinker import users
from .nuralinker import sessions
from .nuralinker import linkers
from .nuralinker import auth
from .nuralinker import path
from .linker import Linker
import os
import shutil
from .user import User
from .user import Session
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from .tmplt import Tmplt
from zipfile import ZipFile

"""
auth code must run for every view and there does not seem to be a way to
route all urls through a single function, it pains me but with this 
framework, dirty code is required, I've made it as clean as possible
"""
def browse(request):
    # auth code -- this block must be used as a whole for proper function
    suc, ses = auth(request)
    if not suc:
        return ses  # ses is response if not suc
    # auth code end

    browse = Tmplt('browse/browse.html', {'linkers': 'No linkers here yet, make one!', 'user': 'everyone'})
    for linker in linkers:
        linker = linkers[linker]
        subtbl = {'name': linker['name'], 'owner': linker['owner'], 'desc': linker['desc']}
        tlinker = Tmplt('browse/linker.html', subtbl)
        browse.ins('linkers', tlinker)
    return base('browse', browse, ses)


def base(title, page, ses=False):
    if ses and ses['uname']:
        uname = ses['uname']
        logout = 'Logout'
    else:
        uname = ''
        logout = ''
    base = Tmplt('base.html', {'title': 'Nurallinker ' + title, 'page': page, 'uname': uname, 'logout': logout})
    r = HttpResponse(base.gtxt())
    if ses:
        r.set_cookie('sestok', ses['token'])
    return r


def about(request):
    # auth code -- this block must be used as a whole for proper function
    suc, ses = auth(request)
    if not suc:
        return ses  # ses is response if not suc
    # auth code end
    return base('about', Tmplt('about/about.html', {}), ses)


def docs(request):
    # auth code -- this block must be used as a whole for proper function
    suc, ses = auth(request)
    if not suc:
        return ses  # ses is response if not suc
    # auth code end
    return base('about', Tmplt('about/docs.html', {}), ses)

@csrf_exempt
def manage(request):
    # auth code -- this block must be used as a whole for proper function
    suc, ses = auth(request)
    if not suc:
        return ses  # ses is response if not suc
    # auth code end

    if ses['uname']:
        if request.method == 'POST':
            linker = request.POST['linker']
            if linker.startswith('.') or '/' in linker or len(linker) > 32:
                manage = Tmplt('manage/manage.html',
                               {'cerr': 'Linker names may not start with a dot or contain a forward slash',
                                'linkers': 'No linkers yet, create one!'}, ses)
            else:
                return redirect('/p/' + linker)
        else:
            manage = Tmplt('manage/manage.html', {'cerr': '', 'linkers' : 'No linkers yet, create one!'}, ses)

        ulinkers = users[ses['uname']]['linkers']
        for klinker in ulinkers:
            linker = ulinkers[klinker]
            tlinker = Tmplt('manage/linker.html',
                            {'owner': ses['uname'], 'name': linker['name'], 'desc': linker['desc']})
            manage.ins('linkers', tlinker)
        return base('Manage', manage, ses)
    else:
        return redirect('/login')


@csrf_exempt
def login(request):
    # auth code -- this block must be used as a whole for proper function
    suc, ses = auth(request)
    if not suc:
        return ses  # ses is response if not suc
    # auth code end

    if ses['uname']:
        return redirect('/manage')

    if request.method == 'POST':
        post = request.POST
        uname = post['uname']
        passwd = post['passwd']
        cpasswd = post['cpasswd']
        if cpasswd:  # this is a password confirmation / user creation
            if uname in users:  # this user has already been created
                login = Tmplt('login.html', {'uerr': 'It looks like someone else just took that username',
                                             'perr': '', 'pcon': '',
                                             'uname': '', 'cpasswd': ''}, ses)
            elif passwd == cpasswd:  # create this user
                user = User['new'](uname)
                User['setpasswd'](user, passwd)
                users[uname] = user
                ses['uname'] = uname
                user['sess'][ses['token']] = True
                return redirect('/manage')
            else:  # passwords do not match
                login = Tmplt('login.html',
                              {'uerr': '', 'perr': 'The passwords do not mach',
                               'pcon': 'Confirm the last password to create this user',
                               'uname': uname, 'cpasswd': passwd}, ses)
        elif uname in users:
            user = users[uname]
            if User['auth'](user, post['passwd']):  # successful login
                ses['uname'] = uname
                user['sess'][ses['token']] = True
                return redirect('/manage')
            else:  # the password is wrong!
                login = Tmplt('login.html',
                              {'uerr': '', 'perr': 'Wrong password!', 'pcon': '',
                               'uname': uname, 'cpasswd': ''}, ses)
        else:  # the username is not registered
            # check username and password for validity
            unl = len(uname)
            if unl > 32:
                uerr = 'Your name must be at most 32 characters'
            elif unl < 1:
                uerr = 'You must chose a name'
            elif uname.startswith('.'):  # user dir cannot be hidden or climb to the parent
                uerr = 'Your name must not start with a dot'
            elif '/' in uname:  # user dir will be a single directory
                uerr = 'Your name must not contain a forward slash'

            login = Tmplt('login.html',
                          {'uerr': 'This user is not yet registered', 'perr': '',
                           'pcon': 'Confirm your password to create this user',
                           'uname': uname, 'cpasswd': passwd}, ses)
    else:
        login = Tmplt('login.html', {'uerr': '', 'perr': '', 'pcon':'',
                               'uname': '', 'cpasswd': ''}, ses)
    return base('login', login, ses)


def user(request, user):
    # auth code -- this block must be used as a whole for proper function
    suc, ses = auth(request)
    if not suc:
        return ses  # ses is response if not suc
    # auth code end
    browse = Tmplt('browse/browse.html', {'linkers': 'No linkers here yet', 'user': user})
    if user not in users:
        return HttpResponseNotFound("That user does not exist")
    user = users[user]
    ulkrs = user['linkers']
    for lpath in ulkrs:
        linker = ulkrs[lpath]
        subtbl = {'name': linker['name'], 'owner': linker['owner'], 'desc': linker['desc']}
        tlinker = Tmplt('browse/linker.html', subtbl)
        browse.ins('linkers', tlinker)
    return base('browse', browse, ses)

lsess = {} # store the linker sessions

@csrf_exempt
def linker(request, user, linker):
    # auth code -- this block must be used as a whole for proper function
    suc, ses = auth(request)
    if not suc:
        return ses  # ses is response if not suc
    # auth code end

    # get key
    lseskey = ses['token'] + '/' + user + '/' + linker
    if lseskey in lsess:
        lses = lsess[lseskey]
    else:
        lses = Linker['linkses'](user, linker)
        lsess[lseskey] = lses

    if request.method == 'POST':
        post = request.POST
        qesresource = post['qesr']
        ansresource = post['ansr']

        qestype = post['qest']
        anstype = post['anst']


        if qestype == 'a':
            qestmplt = Tmplt('linker/qes/audio.html', {'resource': qesresource, 'user': user, 'linker': linker})
        elif qestype == 'i':
            qestmplt = Tmplt('linker/qes/image.html', {'resource': qesresource, 'user': user, 'linker': linker})
        elif qestype == 't':
            qestmplt = Tmplt('linker/qes/text.html', {'resource': qesresource})

        if anstype == 'a':
            anstmplt = Tmplt('linker/qes/audio.html', {'resource': ansresource, 'user': user, 'linker': linker})
        elif anstype == 'i':
            anstmplt = Tmplt('linker/qes/image.html', {'resource': ansresource, 'user': user, 'linker': linker})
        elif anstype == 't':
            anstmplt = Tmplt('linker/qes/text.html', {'resource': ansresource})
        elif anstype == 'o':
            anstmplt = Tmplt('linker/qes/text.html', {'resource': ansresource})

        if 'ans' not in post or not post['ans']:
            result = 'Skipped'
            resclass = 'icor'
            dodds = 1
        elif post['ans'] == ansresource:  # correct
            result = 'Correct!'
            resclass = 'cor'
            dodds = - 1
        else:  # incorrect
            print('"' + post['ans'] + '"' + ansresource + '"')
            result = 'Incorrect'
            resclass = 'icor'
            dodds = 1



        ansnodes = lses['ansnodes']
        qesnodes = lses['qesnodes']
        master = True
        for ansnode in ansnodes:
            if ansnode['odds'] > 1:
                master = False
            if ansnode['resource'] == ansresource:
                ansnode['odds'] += dodds
                lses['aos'] += dodds
                if ansnode['odds'] < 1:
                    ansnode['odds'] = 1
                    lses['aos'] += 1
        for qesnode in qesnodes:
            if qesnode['odds'] > 1:
                master = False
            if qesnode['resource'] == qesresource:
                qesnode['odds'] += dodds
                lses['qos'] += dodds
                if qesnode['odds'] < 1:
                    qesnode['odds'] = 1
                    lses['qos'] += 1

        if master:
            del lsess[lseskey]
            page = Tmplt('linker/finish.html', {'user': user, 'linker': linker}, ses)
        else:
            page = Tmplt('linker/result.html', {'qes': qestmplt, 'ans': anstmplt, 'user': user, 'linker': linker,
                                            'result': result, 'resclass': resclass}, ses)
    else:
        # generate and return a question
        next = Linker['next'](lses)
        # next {'qes', 'anss', 'ans'} # node {'type': 'i', 'resource', 'id', 'odds'}
        qes = next['qes']
        ans = next['ans']
        anss = next['anss']

        anstype = ans['type']
        qestype = qes['type']

        page = Tmplt('linker/ask.html', {'ansr': ans['resource'], 'qesr': qes['resource'],
                                         'anst': ans['type'], 'qest': qes['type'], 'id': ans['id']}, ses)

        if qestype == 'a':
            anstmplt = Tmplt('linker/qes/audio.html', {'resource': qes['resource'], 'user': user, 'linker': linker})
            page.ins('qes', anstmplt)
        elif qestype == 'i':
            anstmplt = Tmplt('linker/qes/image.html', {'resource': qes['resource'], 'user': user, 'linker': linker})
            page.ins('qes', anstmplt)
        elif qestype == 't':
            anstmplt = Tmplt('linker/qes/text.html', {'resource': qes['resource']})
            page.ins('qes', anstmplt)

        if anstype == 'a':
            for opt in anss:
                anstmplt = Tmplt('linker/ans/audio.html', {'resource': opt['resource'], 'user': user, 'linker': linker})
                page.ins('anss', anstmplt)
        elif anstype == 'i':
            for opt in anss:
                anstmplt = Tmplt('linker/ans/image.html', {'resource': opt['resource'], 'user': user, 'linker': linker})
                page.ins('anss', anstmplt)
        elif anstype == 't':
            for opt in anss:
                anstmplt = Tmplt('linker/ans/text.html', {'resource': opt['resource']})
                page.ins('anss', anstmplt)
        elif anstype == 'o':
            anstmplt = Tmplt('linker/ans/open.html', {})
            page.ins('anss', anstmplt)


    return base('session', page, ses)


def download(request, user, linker):
    # adapted from https://stackoverflow.com/a/36394206/4088794
    if user.startswith('.') or '/' in user or linker.startswith('.') or '/' in linker:
        return HttpResponseForbidden('Bad path')
    dl_path = os.path.join(path, 'linkers', user, linker) + '.zip'
    if os.path.exists(dl_path):
        with open(dl_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/zip")
            response['Content-Disposition'] = 'inline; ' + urllib.parse.urlencode({'filename': linker + '.zip'})
            return response
    return HttpResponseNotFound("That linker does not exist")

def resource(request, user, linker, type, file):
    # adapted from https://stackoverflow.com/a/36394206/4088794
    if user.startswith('.') or '/' in user or linker.startswith('.') or '/' in linker \
            or type.startswith('.') or '/' in type or file.startswith('.') or '/' in file:
        return HttpResponseForbidden('Bad path')
    dl_path = os.path.join(path, 'linkers', user, linker, type, file)
    if file.endswith('.jpeg') or file.endswith('.jpg'):
        ext = 'jpeg'
    elif file.endswith('.png'):
        ext = 'png'
    elif file.endswith('.mp3'):
        ext = 'mpeg'
    elif file.endswith('.txt'):
        ext = 'plain'

    if os.path.exists(dl_path):
        with open(dl_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type=type + "/" + ext)
            response['Content-Disposition'] = 'inline; ' + urllib.parse.urlencode({'filename': file})
            return response
    return HttpResponseNotFound("That file does not exist")

@csrf_exempt
def delete(request, linker):
    # auth code -- this block must be used as a whole for proper function
    suc, ses = auth(request)
    if not suc:
        return ses  # ses is response if not suc
    # auth code end
    if linker.startswith('.') or '/' in linker or len(linker) > 32:
        return HttpResponseForbidden('Bad linker name')

    uname = ses['uname']
    if uname:
        lkey = uname + '/' + linker
        plinker = os.path.join(path, 'linkers', uname, linker)
        if request.method == 'POST':
            if request.POST['ans'] == 'act':
                if os.path.exists(plinker):
                    shutil.rmtree(plinker)
                    os.remove(plinker + '.zip')
                    del linkers[lkey]
                    del users[uname]['linkers'][lkey]
            return redirect('/manage')
        else:
            con = Tmplt('manage/confirm.html', {'qus': 'Delete linker ' + linker + '?', 'act': 'Delete'}, ses)
            return base('Delete?', con, ses)
    else:
        return redirect('/login')

@csrf_exempt
def update(request, linker):
    # auth code -- this block must be used as a whole for proper function
    suc, ses = auth(request)
    if not suc:
        return ses  # ses is response if not suc
    # auth code end
    if linker.startswith('.') or '/' in linker or len(linker) > 32 or len(linker) < 1:
        return HttpResponseForbidden('Bad linker name')
    uname = ses['uname']
    if uname:
        lkey = uname + '/' + linker
        plinker = os.path.join(path, 'linkers', uname, linker)
        if request.method == 'POST':
            if os.path.exists(plinker):
                shutil.rmtree(plinker)
                os.remove(plinker + '.zip')
                del linkers[lkey]
                del users[uname]['linkers'][lkey]
            udir = os.path.join(path, 'linkers', uname)
            ldir = os.path.join(udir, linker)
            zip = ldir + '.zip'

            if not os.path.exists(udir):
                os.mkdir(udir)
            with open(zip, 'wb') as dest:
                for chunk in request.FILES['zip'].chunks():
                    dest.write(chunk)

            zf = ZipFile(zip, 'r')
            zf.extractall(ldir)
            zf.close()
            # check if likner is valid, and has no extra files

            valid, err = Linker['validate'](uname, linker)

            if not valid:
                shutil.rmtree(plinker)
                os.remove(plinker + '.zip')
                con = Tmplt('manage/update.html', {'linker': linker, 'err': err}, ses)
                return base('Update', con, ses)

            #  register the linkers in the nurallink objects

            set, err = Linker['settings'](uname, linker)
            desc = set['desc']
            print('upload successful, linking linker')
            nlinker = Linker['new'](uname, linker, desc)
            linkers[lkey] = nlinker
            users[uname]['linkers'][lkey] = nlinker

            return redirect('/manage')
        else:
            con = Tmplt('manage/update.html', {'linker': linker, 'err': ''}, ses)
            return base('Update', con, ses)
    else:
        return redirect('/login')


def theme(request):
    resp = HttpResponse(Tmplt('theme.css', {}).gtxt())
    resp['Content-Type'] = 'text/css'
    return resp

def audio(request):
    resp = HttpResponse(Tmplt('audio.js', {}).gtxt())
    resp['Content-Type'] = 'text/javascript'
    return resp

def logout(request):
    # auth code -- this block must be used as a whole for proper function
    suc, ses = auth(request)
    if not suc:
        return ses  # ses is response if not suc
    # auth code end

    if ses['uname']:  # if the user is logged in
        user = users[ses['uname']]
        ses['uname'] = ''
        del user['sess'][ses['token']]

    return redirect('/')