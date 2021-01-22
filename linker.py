import os
import random
from .nuralinker import path

defodds = 2

def gpath(owner, lname):
    return os.path.join(path, 'linkers', owner, lname)


def nlinker(owner, name, desc):
    return {'owner': owner, 'name': name, 'resource': owner + '/' + name, 'desc': desc}

def settings(owner, lname):
    path = gpath(owner, lname)

    fsettings = open(path + '/settings.txt', 'r')
    lines = fsettings.readlines()
    fsettings.close()

    s = {}
    for line in lines:
        l = line.replace(' ', '')  # remove any spaces
        l = l.replace('\t', '')  # remove any spaces
        l = l.replace('\n', '')  # remove the newline
        ll = len(l)
        if ll == 0 or l[0] == '#':
            pass
        elif l[0] == 'q':
            if ll > 4:
                return False, 'q is too long, should have 3 switches'
            if ll < 4:
                return False, 'q is too short, should have 3 switches'
            s['q'] = {'i': l[1] == '+', 'a': l[2] == '+', 't': l[3] == '+'}

        elif l[0] == 'a':
            if ll > 5:
                return False, 'a is too long, should have 4 switches'
            if ll < 4:
                return False, 'a is too short, should have 4 switches'
            s['a'] = {'i': l[1] == '+', 'a': l[2] == '+', 't': l[3] == '+', 'o': l[4] == '+'}
        elif l[0] == 'd':
            s['desc'] = line[1:]

    for line in lines:
        l = line.replace(' ', '')  # remove any spaces
        l = l.replace('\t', '')  # remove any spaces
        l = l.replace('\n', '')  # remove the newline
        ll = len(l)
        if ll == 0 or l[0] == '#':
            pass
        elif l[0] == 'c':
            if ll > 4:
                return False, 'c is too long, should have 3 digits'
            if ll < 4:
                return False, 'c is too short, should have 3 digits'
            try:
                i = l[1] if s['a']['i'] else 2
                a = l[2] if s['a']['a'] else 2
                t = l[3] if s['a']['t'] else 2
                s['c'] = {'i': int(i), 'a': int(a), 't': int(t)}
            except ValueError:
                return False, 'c should have 3 digits, no other non-space characters'
            if s['c']['i'] < 2 or s['c']['i'] < 2 or s['c']['i'] < 2:
                return False, 'c should have 3 digits from 2 to 9'
    if 'q' not in s:
        return False, 'q (question) missing'
    if 'a' not in s:
        return False, 'a (answer) missing'
    if 'c' not in s:
        return False, 'c (choose) missing'
    if 'desc' not in s:
        return False, 'd (description) missing'

    return s, 0


def validate(owner, lname):
    path = gpath(owner, lname)
    expect = [['d', 'image'], ['d', 'audio'], ['d', 'text'], ['f', 'settings.txt']]
    files = os.listdir(path)

    for e in expect:
        if e[1] in files:
            files.remove(e[1])
        else:
            return False, e[1] + ' is not present, it should be at the root of the zip'

    if len(files) > 0:
        return False, files[0] + ' should not be in the zip'

    pimage = path + '/image'
    paudio = path + '/audio'
    ptext = path + '/text'
    psettings = path + '/settings.txt'

    if not os.path.isdir(pimage):
        return False, 'image should be a directory'
    if not os.path.isdir(paudio):
        return False, 'audio should be a directory'
    if not os.path.isdir(ptext):
        return False, 'text should be a directory'
    if not os.path.isfile(psettings):
        return False, 'settings.txt should be a file'

    images = os.listdir(path + '/image')
    for file in images:
        ext = file.split('.')[-1]
        if ext != 'jpeg' and ext != 'jpg' and ext != 'png':
            return False, 'image format not allowed: .' + ext
    audios = os.listdir(path + '/audio')
    for file in audios:
        ext = file.split('.')[-1]
        if ext != 'mp3':
            return False, 'audio format not allowed: .' + ext
    texts = os.listdir(path + '/text')
    for file in texts:
        ext = file.split('.')[-1]
        if ext != 'txt':
            return False, 'text format not allowed: .' + ext

    cfg, err = settings(owner, lname)
    if not cfg:
        return False, "Error in settings: " + err

    # look for a question for which there is no answer in an enabled answere category
    qess = {}  # all questions, a dict will not store duplicates
    anss = {}  # all answers
    manss = []  # missing answers

    # collect all questions
    if cfg['q']['i']:
        for i in images:
            qess[i.split('.')[0]] = 0
    if cfg['q']['a']:
        for a in audios:
            qess[a.split('.')[0]] = 0
    if cfg['q']['t']:
        for t in texts:
            qess[t.split('.')[0]] = 0
    # collect all answers
    if cfg['a']['i']:
        for i in images:
            anss[i.split('.')[0]] = 0
    if cfg['a']['a']:
        for a in audios:
            anss[a.split('.')[0]] = 0
    if cfg['a']['t']:
        for t in texts:
            anss[t.split('.')[0]] = 0
    if cfg['a']['o']:  # open answers also correspond to text files
        for t in texts:
            anss[t.split('.')[0]] = 0
    # check for missing answers
    if cfg['a']['i']:
        qis = {}
        for i in images:
            qis[i.split('.')[0]] = 0
        for q in qess:
            if q not in qis:
                manss.append(q + ' is a question but is not an image answer')
    if cfg['a']['a']:
        qas = {}
        for a in audios:
            qas[a.split('.')[0]] = 0
        for q in qess:
            if q not in qas:
                manss.append(q + ' is a question but is not an audio answer')
    if cfg['a']['t']:
        qts = {}
        for t in texts:
            qts[t.split('.')[0]] = 0
        for q in qess:
            if q not in qts:
                manss.append(q + ' is a question but is not a text answer')
    # check for missing questions
    if cfg['q']['i']:
        qis = {}
        for i in images:
            qis[i.split('.')[0]] = 0
        for q in anss:
            if q not in qis:
                manss.append(q + ' is an answer but is not an image question')
    if cfg['q']['a']:
        qas = {}
        for a in audios:
            qas[a.split('.')[0]] = 0
        for q in anss:
            if q not in qas:
                manss.append(q + ' is an answer but is not an audio question')
    if cfg['q']['t']:
        qts = {}
        for t in texts:
            qts[t.split('.')[0]] = 0
        for q in anss:
            if q not in qts:
                manss.append(q + ' is an answer but is not a text question')
    err = ''
    for m in manss:
        err = err + m + ', '

    if err:
        return False, err

    imageids = {}
    for name in images:
        imageids[name.split('.')[0]] = name
    audioids = {}
    for name in audios:
        audioids[name.split('.')[0]] = name
    textids = {}
    for name in texts:
        textids[name.split('.')[0]] = name

    err = ''
    if cfg['a']['i'] and cfg['c']['i'] > len(imageids):
        err += 'choose setting for images (' + str(cfg['c']['i']) + ') is greater than the number of image answers (' \
               + str(len(imageids)) + '), '
    if cfg['a']['a'] and cfg['c']['a'] > len(audioids):
        err += 'choose setting for audios (' + str(cfg['c']['a']) + ') is greater than the number of audio answers (' \
               + str(len(audioids)) + '), '
    if cfg['a']['t'] and cfg['c']['t'] > len(textids):
        err += 'choose setting for texts (' + str(cfg['c']['t']) + ') is greater than the number of text answers (' \
               + str(len(textids)) + ')'

    if err:
        return False, err

    return True, 0

tfcc = {} # text file content cache
def tfc(owner, lname, t):
    tfp = os.path.join(path, 'linkers', owner, lname, 'text', t)
    if tfp in tfcc:
        return tfcc[tfp]
    else:
        tf = open(tfp, 'r')
        tfcc[tfp] = tf.read().strip()
        tf.close()
        return tfcc[tfp]


def linkses(owner, lname):
    path = gpath(owner, lname)

    ansnodes = []
    qesnodes = []

    images = os.listdir(path + '/image')
    audios = os.listdir(path + '/audio')
    texts = os.listdir(path + '/text')

    cfg, err = settings(owner, lname)

    qos = 0
    aos = 0

    # collect all questions
    if cfg['q']['i']:
        for i in images:
            qos += defodds
            qesnodes.append({'type': 'i', 'resource': 'image/' + i, 'id': i.split('.')[0], 'odds': defodds})
    if cfg['q']['a']:
        for a in audios:
            qos += defodds
            qesnodes.append({'type': 'a', 'resource': 'audio/' + a, 'id': a.split('.')[0], 'odds': defodds})
    if cfg['q']['t']:
        for t in texts:
            qos += defodds
            qesnodes.append({'type': 't', 'resource': tfc(owner, lname, t), 'id': t.split('.')[0], 'odds': defodds})
    # collect all answers
    if cfg['a']['i']:
        for i in images:
            aos += defodds
            ansnodes.append({'type': 'i', 'resource': 'image/' + i, 'id': i.split('.')[0], 'odds': defodds})
    if cfg['a']['a']:
        for a in audios:
            aos += defodds
            ansnodes.append({'type': 'a', 'resource': 'audio/' + a, 'id': a.split('.')[0], 'odds': defodds})
    if cfg['a']['t']:
        for t in texts:
            aos += defodds
            ansnodes.append({'type': 't', 'resource': tfc(owner, lname, t), 'id': t.split('.')[0], 'odds': defodds})
    if cfg['a']['o']:  # open answers also correspond to text files
        for t in texts:
            aos += defodds
            ansnodes.append({'type': 'o', 'resource': tfc(owner, lname, t), 'id': t.split('.')[0], 'odds': defodds})

    return {'qesnodes': qesnodes, 'ansnodes': ansnodes, 'owner': owner, 'lname': lname, 'choose': cfg['c'],
            'qos': qos, 'aos': aos, 'answer': cfg['a'], 'question': cfg['q']}

def next(linkses):
    path = gpath(linkses['owner'], linkses['lname'])
    qesnodes = linkses['qesnodes']
    ansnodes = linkses['ansnodes']  # {'type': 'i', 'resource', 'id', 'odds'}

    choose = linkses['choose']  # {'i', 'a', 't'}
    answer = linkses['answer']
    question = linkses['question']
    qos = linkses['qos']
    aos = linkses['aos']

    qes = random.randint(0, 1)
    if qes:
        sum = qos
        nodes = qesnodes
    else:
        sum = aos
        nodes = ansnodes

    pick = random.randint(0, sum - 1)
    for node in nodes:
        odds = node['odds']
        if pick < odds:
            cnode = node
            break
        else:
            pick -= odds

    if qes:
        # question is picked already
        qesnode = cnode
        atypes = []
        if answer['i']:
            atypes.append('i')
        if answer['a']:
            atypes.append('a')
        if answer['t']:
            atypes.append('t')
        if answer['o']:
            atypes.append('o')

        atype = qesnode['type']
        atypes.remove(atype)
        if atype == 't' and 'o' in atypes:
            atypes.remove('o')

        ctype = atypes[random.randint(0, len(atypes) - 1)] # choosen type

        # shuffle our nodes, we will take tha last under each id
        random.shuffle(ansnodes)
        candidates = {}
        for an in ansnodes:
            if an['type'] == ctype:
                if an['id'] == qesnode['id']:
                    ansnode = an
                candidates[an['id']] = an
        del candidates[ansnode['id']]  # delete the already chosen candidate
        carr = []
        for an in candidates:
            carr.append(candidates[an])
        random.shuffle(carr)
        choises = [ansnode]
        if ctype != 'o':
            for i in range(choose[ctype] - 1):
                choises.append(carr[i])
        random.shuffle(choises)
        # qesnode, choises
    else:
        # ans is picked already
        ansnode = cnode
        atype = ansnode['type']

        # shuffle our nodes, we will take tha last under each id
        random.shuffle(ansnodes)
        candidates = {}
        for an in ansnodes:
            if an['type'] == atype:
                candidates[an['id']] = an
        del candidates[ansnode['id']]  # delete the already chosen candidate
        carr = []
        for an in candidates:
            carr.append(candidates[an])
        random.shuffle(carr)
        choises = [ansnode]
        if atype != 'o':
            for i in range(choose[atype] - 1):
                choises.append(carr[i])
        random.shuffle(choises)

        # choose the question type
        atypes = []
        if question['i']:
            atypes.append('i')
        if question['a']:
            atypes.append('a')
        if question['t']:
            atypes.append('t')
        if atype == 'o':
            if 't' in atypes:
                atypes.remove('t')
        else:
            atypes.remove(atype)
        ctype = atypes[random.randint(0, len(atypes) - 1)]  # chosen type
        # grab one of the ctype questions for this answer
        candidates = []
        for qn in qesnodes:
            if qn['type'] == ctype and qn['id'] == ansnode['id']:
                candidates.append(qn)
                break
        qesnode = candidates[random.randint(0, len(candidates) - 1)]  # chosen question
    return {'qes': qesnode, 'anss': choises, 'ans': ansnode}

Linker = {'new': nlinker, 'validate': validate, 'settings': settings, 'linkses': linkses, 'next': next}