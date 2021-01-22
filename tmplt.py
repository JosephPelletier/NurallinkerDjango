# a basic template system by joseph pelletier
import html
from .nuralinker import path
from .user import Session
tmplt_path = path + 'tmplts/'

class Tmplt:

    def __init__(self, path, subtbl, session=False):
        self.path = path
        file = open(tmplt_path + path)
        self.wtxt = file.read() #working text
        file.close()
        if session:
            subtbl['sestok'] = '<input type="hidden" name="sestok" value="' + session['token'] + '">'
        self.subtbl = subtbl #variable substitution table
        self.ipts = {}
        self.txt = False

    def ins(self, point, content):
        ipt = '{% ' + point + ' %}'
        if self.txt != False:
            raise ValueError(ipt + ' cannot be used, txt already finalized by gtxt()')
        if not ipt in self.wtxt:
            raise ValueError(ipt + ' does not exist in file ' + self.path)
        if type(content) is Tmplt:
            content = content.gtxt()
        self.wtxt = self.wtxt.replace(ipt, content + ipt)
        self.ipts[ipt] = True

    def gtxt(self):
        if self.txt != False:
            return self.txt

        wtxt = self.wtxt
        for ipt in self.ipts.keys():
            wtxt = wtxt.replace(ipt, '')
        for subk in self.subtbl.keys():
            sub = self.subtbl[subk]
            if type(sub) is Tmplt:
                sub = sub.gtxt()
            elif subk != 'sestok':
                sub = html.escape(sub)
            wtxt = wtxt.replace('{% ' + subk + ' %}', sub)

        self.txt = wtxt
        return wtxt
