#!/usr/local/bin/python
import sys,json,re,os,errno
from optparse import OptionParser

class ArrayOut():
    _arr=None
    _buf=None

    def __init__(self):
        self._arr=[]
        self._buf=""

    def write(self,txt):
        tmparr=txt.split('\n')

        for idx in range(len(tmparr)-1):
            line=tmparr[idx]
            self._buf+=line
            self._arr.append(self._buf.split('\t'))
            self._buf=''

        self._buf+=tmparr[-1]

    def getJSON(self,pretty=False):
        if pretty:
            return json.dumps(self._arr, indent=4, separators=(',', ': '))
        else:
            return json.dumps(self._arr)


class PPar :
    # _m is the method of parsing: 'a'uto, 'p'ython, 's'tring, 'j'son
    _m = None
    _pln = None # ref to the PPLine object

    def __init__(self, m, pln) :
        self._m = m
        self._pln = pln

    def __getitem__(self, index) :
        if self._pln._att[index] != self._m :
            self._pln._ppts[index] = self._parse(self._pln._pts[index])
            self._pln._att[index] = self._m
        return self._pln._ppts[index]

    def _parse(self,pt) :
        if self._m == 's' :
            return pt
        
        obj_j = None

        obj_p = None
        if self._m == 'a' or self._m == 'p' :
            try :
                obj_p = eval(pt)
            except :
                pass
        if self._m == 'p' :
            return obj_p

        if isinstance(obj_p, str) :
            return pt

        if obj_p is not None :
            return obj_p

        if self._m == 'a' or self._m == 'j' :
            try :
                obj_j = json.loads(pt)
            except :
                pass
        if self._m == 'j' or obj_j is not None :
            return obj_j

        return pt


class PPLine :
    _pts = None
    _att = None
    _ppts = None
    _mths = None
    _a = None

    s = None
    p = None
    j = None


    def __init__(self, line_parts) :
        self._pts = line_parts
        self._ppts = [None] * len(line_parts)
        self._att = [None] * len(line_parts)
        self.s = PPar('s', self)
        self.p = PPar('p', self)
        self.j = PPar('j', self)
        self._a = PPar('a', self)

    def __getitem__(self, index) :
        if self._att[index] != 'a' :
            self._ppts[index] = self._a[index]
            self._att[index] = 'a'
        return self._ppts[index]

    def __len__(self) :
        return len(self._pts)

    def __str__(self) :
        return str(self._pts)




ERR_MSG_QSIZE=10
TAB_EQUIV="~"

def help_msg():

    s="<<< How Command Options Work in the Code >>>"
    
    total=len(s)
    print
    print s
    print 
    print
   

    lns=[
        (0,"<exec> [b]eginning process","b"),
        (0,"<eval> and <print> [i]nitial lines","i"),
        (0,"for each line [f]rom input:","f"),
        (1,"load line as c",None),
        (1,"<exec> [p]reparation codes","p"),
        (1,"<eval> [w]here condition","w"),
        (1,"if condition is true:",None),
        (2,"<eval> and <print> [s]elect","s"),
        (2,"<exec> [u]pdate code","u"),
        (1,"end if",None),
        (0,"end for",None),
        (0,"<exec> [e]nding proecess","e"),
        (0,"<eval> and <print> [l]ast lines","l")
     ]

    print "Code runs as follows:"    

    print "="*total

    ss="Intelligent Import"
    print ss+"."*(total-3-len(ss))+"[ --imp ]"
    print 
    
    for ln in lns:
        bb=ln[0]*4+2
        ss=" "*bb+ln[1]
        if ln[2]:
            ss+="."*(total-bb-len(ln[1]))+"[ -"+ln[2]+" ]"

        print ss

    print "="*total
    print


def slo_func(fin, imps=[],ini_arr=[], bp=None, whr=None, prep=None, sel_arr=[], post=None, ep=None, last_arr=[],fout=None):

    if fout is None:
        rfout=sys.stdout
    else:
        rfout=fout

    err_cnts={}
    ln_cnt=0

    acnt=None

    gmap={}
    lmap={}

    out_lines=[]
    err_msgs=[]

    exec 'import sys,json,re,math' in gmap

    # Customized Import
    if imps:
        for imp in imps:
            exec 'sys.path.append("'+imp[0]+'")' in gmap
            if imp[2] is None:
                exec 'import '+imp[1] in gmap
            else:
                exec 'import '+imp[1]+' as '+imp[2] in gmap


    # Exec BeginProc
    if bp:
        try:
            exec bp in gmap
        except Exception as e:
            err_msgs.append("[Error::BeginProcess]"+str(e))


    # Eval Initials

    iselobjs=[]
    for isel in ini_arr:
        opt=None
        try:
            opt=eval(isel,gmap,lmap)
        except Exception as e:
            err_cnts['InitStrError'] = err_cnts.get('InitStrError',0) + 1

            if len(err_msgs)<ERR_MSG_QSIZE:
                err_msgs.append("[Error::InitStr] Line : " +str(e) + " : " + isel)

        iselobjs.append(opt)

    if len(iselobjs)>0:
        print>>rfout,("\t".join([str(x) for x in iselobjs]))

        

    for line in fin:
        lmap={}


        # Loading c
        sline=line.strip().split("\t")        
        ln_cnt+=1
        c=PPLine(sline)
        #for pt in sline:
        #    c.append(parse(pt))
        
            
        gmap["c"]=c #lmap["c"]

        # Eval Prep
        if prep:
            try:
                exec prep in gmap,lmap
                # update
                gmap.update({x:lmap[x] for x in lmap if x in gmap})

            except Exception as e:
                err_cnts['PrepStrError'] = err_cnts.get('PrepStrError',0) + 1
                if len(err_msgs)<ERR_MSG_QSIZE:
                    err_msgs.append("[Error::PrepStr] Line " + str(ln_cnt) + " : " + str(e) + " : " + prep)


        # Eval Where condition
        wv=False

        if whr: 
            try:
                wv=eval(whr, gmap, lmap)
            except Exception as e:
                err_cnts['WhereStrError'] = err_cnts.get('WhereStrError',0) + 1
                if len(err_msgs)<ERR_MSG_QSIZE:
                    err_msgs.append("[Error::WhereStr] Line " + str(ln_cnt) + " : " +str(e) + " : " + whr)
        else:
            wv=True

            
        if wv:
            selobjs=[]
                
            # Eval Select String                
                
            for sel in sel_arr:
                opt=None
                try:
                    opt=eval(sel,gmap,lmap)
                except Exception as e:
                    err_cnts['SelectStrError'] = err_cnts.get('SelectStrError',0) + 1
                        
                    if len(err_msgs)<ERR_MSG_QSIZE:
                        err_msgs.append("[Error::SelectStr] Line " + str(ln_cnt) + " : " +str(e) + " : " + str(sel))
                    
                selobjs.append(opt)

            if len(selobjs)>0:
                print>>rfout,("\t".join([str(x) for x in selobjs]))
                
            if post:
                try:
                    exec post in gmap,lmap
                    # update
                    gmap.update({x:lmap[x] for x in lmap if x in gmap})

                except Exception as e:
                    err_cnts['PostStrError'] = err_cnts.get('PostStrError',0) + 1
                    if len(err_msgs)<ERR_MSG_QSIZE:
                        err_msgs.append("[Error::PostStr] Line " + str(ln_cnt) + " : " + str(e) + " : " + post)
            
            

    #Eval ep
    if ep:
        try:
            exec ep in gmap
        except Exception as e:
            err_cnts['EndingStrError'] = err_cnts.get('EndingStrError',0) + 1
            if len(err_msgs)<ERR_MSG_QSIZE:
                        err_msgs.append("[Error::EndStr] " + str(e) + " : " + ep)

    # Eval Last
    lselobjs=[]
    for lsel in last_arr:
        opt=None
        try:
            opt=eval(lsel,gmap,lmap)
        except Exception as e:
            err_cnts['LastStrError'] = err_cnts.get('LastStrError',0) + 1

            if len(err_msgs)<ERR_MSG_QSIZE:
                err_msgs.append("[Error::LastStr] Line " + str(ln_cnt) + " : " +str(e) + " : " + lsel)

        lselobjs.append(opt)


    if len(lselobjs)>0:
        print>>rfout,("\t".join([str(x) for x in lselobjs]))
        

    oobj={"ln_cnt" : ln_cnt, "err_cnts" : err_cnts, "err_msg_top" : err_msgs, "out" : out_lines}

    return oobj

def parseImp(imp_str):
    imps=[]
    if imp_str:
        for path_alias in imp_str.strip().split(':'):
            pts=path_alias.strip().split('#')
            if len(pts)>=2:
                path="#".join(pts[:-1])
                alias=pts[-1]
            else:
                path=pts[0]
                alias=None
                
            abspath=os.path.abspath(os.path.expanduser(path))
            dirname=os.path.dirname(abspath)
            basename=os.path.basename(abspath)
            modname=basename[:basename.rindex(".py")]
            imps.append((dirname,modname,alias))

    return imps

def main():
    imp_objs=parseImp(options.iimp)
    ini_arr=[]
    if options.iniln:
        ini_arr=options.iniln.strip().split(TAB_EQUIV)
    
    sel_arr=[]
    if options.select:
        if options.select=='*':
            sel_arr=['"\t".join(c.s)']
        else:
            sel_arr=options.select.strip().split(TAB_EQUIV)

    last_arr=[]
    if options.lstln:
        last_arr=options.lstln.strip().split(TAB_EQUIV)

    if options.finput:
        fin=open(options.finput)
    else:
        fin=sys.stdin
    
    if options.jout:
        rout=ArrayOut()
    else:
        rout=sys.stdout

    robj=slo_func(fin,ini_arr=ini_arr,imps=imp_objs,bp=options.bp,whr=options.whr,prep=options.prep,sel_arr=sel_arr,post=options.upgr,ep=options.ep,last_arr=last_arr,fout=rout)

    if options.jout:
        print json.dumps(rout._arr)

    print>>sys.stderr,"Total Lines:",robj["ln_cnt"]

    if sum(robj["err_cnts"].values())>0:
        print>>sys.stderr,"Errors:",json.dumps(robj["err_cnts"])

    if len(robj["err_msg_top"])>0:
        print>>sys.stderr,"Top Error Messages:"
        for emsg in robj["err_msg_top"]:
            print>>sys.stderr,emsg

    if options.finput:
        fin.close()
    

if __name__ == '__main__':
    
    parser = OptionParser()
    parser.add_option("--explain",action="store_true",dest="explain", help="explain how the code works")
    
    parser.add_option("--json_out",action="store_true",dest="jout",help="print results with json")
    
    parser.add_option("--errmsg",action="store",type="int",dest="emsg",help="number of the first N error messages to print", default=10)
    parser.add_option("--tabeq",action="store",type="string",dest="tabeq",help="TAB-equiv for eval strings", default='~')
    
    parser.add_option("--imp", action="store", type="string", dest="iimp",default=None,help="intelligent import")

    parser.add_option("-b", action="store", type="string", dest="bp",default=None,help="beginning process")
    parser.add_option("-i", action="store", type="string", dest="iniln",default=None,help="initial lines")
    parser.add_option("-f", action="store", type="string", dest="finput",default=None,help="input from")
    parser.add_option("-p", action="store", type="string", dest="prep",default=None,help="preprocess of each line")
    parser.add_option("-w", action="store", type="string", dest="whr",default=None,help="where clause")
    parser.add_option("-s", action="store", type="string", dest="select",default=None,help="select clause")
    parser.add_option("-u", action="store", type="string", dest="upgr",default=None,help="agg-update code of each line")
    parser.add_option("-e", action="store", type="string", dest="ep",default=None,help="ending process")
    parser.add_option("-l", action="store", type="string", dest="lstln",default=None,help="last lines")

    (options, args) = parser.parse_args()

    if options.explain:
        help_msg()
        sys.exit(0)
    

    ERR_MSG_QSIZE=options.emsg
    TAB_EQUIV=options.tabeq

    main()
