#!/usr/local/bin/python
import re,json,sys

__all__=['regex','within','xj']

regex=re.compile

def within(sz):
    tsz=sz.strip()
    if tsz[0]=='(':
        leftinc=False
    elif tsz[0]=='[':
        leftinc=True

    if tsz[-1]==')':
        rightinc=False
    elif tsz[-1]==']':
        rightinc=True

    losz,hisz=tsz[1:-1].strip().split(',')
    if losz in ['None','null','']:
        lo=None
    else:
        lo=float(losz)
    if hisz in ['None','null','']:
        hi=None
    else:
        hi=float(hisz)

    return slice(lo,hi,(leftinc,rightinc))


class xj_rs(object):

    def __init__(self,igen):
        self.igen=igen

    cc=property( lambda rs: xj_cc(rs._val_gen(),[]) )
    
    all=property( lambda rs: [t for t in rs.igen] )

    values=property( lambda rs: [t[0] for t in rs.igen] )

    paths=property( lambda rs: [t[1] for t in rs.igen] )

    json=property( lambda rs: json.dumps([t for t in rs.values]))

    xj=property( lambda rs: xj(rs.values) )

    def __iter__(self):
        return self

    def next(self):
        return self.igen.next()

    def _val_gen(self):
        for item in self.igen:
            yield item[0]


class xj_cc(object):

    def __init__(self,jgen,rlist):
        self.jgen=jgen
        self.rlist=rlist[:]

    def __iter__(self):
        return self

    def next(self):
        jo=self.jgen.next()
        return self._tup_jo_cc(jo)

    def _tup_jo_cc(self,jo):
        tup=tuple()
        tmp_z=xj(jo)

        tmp_z.path_mode=False


        for k in self.rlist:
            tmp_zrs=tmp_z[k]
            crz=tmp_zrs.values
            if len(crz)==0:
                tup+=(None,)
            elif len(crz)==1:
                tup+=(crz[0],)
            else:
                tup+=(crz,)
        return tup

    def __getitem__(self,k):
        return self.__class__(self.jgen,self.rlist+[k])

    def joint_by(self,tchar):
        for jo in self.jgen:
            yield tchar.join([json.dumps(titem) for titem in self._tup_jo_cc(jo)])


class xj(object):
    _dummy_ro_cls=re.compile(r'dummy').__class__

    path_mode=True
    #value_mode=True

    @classmethod
    def is_re_obj(cls,so):
        return isinstance(so,cls._dummy_ro_cls)

    def __init__(self,jobj):
        self.jo=jobj

    def __getitem__(self,k):

        '''
        if not self.path_mode and not self.value_mode:
            raise Exception('what do you expect?')
        '''
        if isinstance(k,tuple):
            gen=self._yd_seq(self.jo,() if self.path_mode else None,k)
        else:
            gen=self._yd_one(self.jo,() if self.path_mode else None,k)

        return xj_rs(gen)


    def _yd_one(self,co,po,k):

        # general jump
        if k==Ellipsis:
            for ko,npo in self._yd_one(co,po,-1j):
                yield ko,npo

        elif isinstance(k,complex):
            for ko,npo in self._jtrans_jo(co,po,int(k.real),int(k.imag),0):
                yield ko,npo

        elif k is None:
            for ko,npo in self._jtrans_jo(co,po,1,0,0):
                yield ko,npo


        # dict type jump
        elif (isinstance(k,str) or isinstance(k,unicode)) and isinstance(co,dict):
            if k in co:
                yield co[k],self.app(po,k)

        elif self.__class__.is_re_obj(k) and isinstance(co,dict): 
            for ko in co:
                if k.match(ko):
                    yield co[ko],self.app(po,ko)


        # list type jump
        elif isinstance(k,int) and isinstance(co,list):
            if 0<=k<len(co):
                yield co[k],self.app(po,k)
            elif -len(co)<k<0:
                yield co[k],self.app(po,len(co)-1+k)
        elif isinstance(k,slice) and isinstance(co,list):
            for idx,ko in [tt for tt in enumerate(co)][k]:
                yield ko,self.app(po,idx)

        # general match
        elif self._match(k,co):
            yield co,po
        
    def app(self,op,nk):
        if op is None:
            return None
        else:
            return op+(nk,)

    def _match(self,tmpl,tobj):

        if isinstance(tobj,str) or isinstance(tobj,unicode):
            # str matches str, set, regex
            if self.__class__.is_re_obj(tmpl):
                return tmpl.match(tobj)
            elif isinstance(tmpl,set):
                return tobj in tmpl
            elif isinstance(tmpl,str)or isinstance(tmpl,unicode):
                return tmpl==tobj

        elif isinstance(tobj,int) or isinstance(tobj,float):
            # number matches number, slice, set
            if isinstance(tmpl,int) or isinstance(tmpl,float):
                return tobj==tmpl
            elif isinstance(tmpl,slice):
                if (
                        isinstance(tmpl.step,str) and 
                        len(tmpl.step)==2 and 
                        tmpl.step[0] in '([' and 
                        tmpl.step[1] in ')]'
                ) :
                    incl=(tmpl.step[0]=='[',tmpl.step[1]==']') 
                else:
                    incl=(True,True)
                return (
                        tmpl.start is None or ( 
                            tobj>tmpl.start or (incl[0] and tobj==tmpl.start)
                        )
                ) and (
                     tmpl.stop is None or (
                            tobj<tmpl.stop or (incl[1] and tobj==tmpl.stop)
                        )
                )
            elif isinstance(tmpl,set):
                return tobj in tmpl

        elif hasattr(tmpl, '__call__'):
            try:
                if tmpl(co):
                    return True
            except Exception as e:
                return False

        elif isinstance(tobj,dict) and isinstance(tmpl,dict):
            return all( 
                any( self._match(tmpl[tmpl_sk],tobj[tsk]) for tsk in tobj if self._match(tmpl_sk,tsk) )
                for tmpl_sk in tmpl
            )

        elif isinstance(tobj,list) and isinstance(tmpl,list):
            return all( 
                any( self._match(tmpl_so,tso) for tso in tobj )
                for tmpl_so in tmpl
            )

        return False
        
    def _yd_seq(self,co,po,seq):

        for k,np in self._yd_one(co,po,seq[0]):
            if len(seq)>1:
                for kk in self._yd_seq(k,np,seq[1:]):
                    yield kk
            else:
                yield k,np

    def _jtrans_jo(self,co,po,least,more,cur):
        if cur>=least and (more<0 or cur<=least+more):
            yield co,po

        if more<0 or least+more-cur>=1:
            if isinstance(co,list):
                for idx,k in enumerate(co):
                    for ko in self._jtrans_jo(k,self.app(po,idx),least,more,cur+1):
                        yield ko
            elif isinstance(co,dict):
                for k in co:
                    for ko in self._jtrans_jo(co[k],self.app(po,k),least,more,cur+1):
                        yield ko


def main():
    
    global z,jo
    z=None
    jo=None

    if options.cli_mode:
        if options.ffile is not None:
            with open(options.ffile) as fin:
                jo=json.load(fin)
                z=xj(jo)

        import cmd
        mmap={
            'bold':'1',
            'dim':'2',
            'underline':'4',
            'blink':'5',
            'reverse':'7',
            'black':'30',
            'red':'31',
            'green':'32',
            'yellow':'33',
            'blue':'34',
            'magenta':'35',
            'cyan':'36',
            'white':'37',
            'bg-black':'40',
            'bg-red':'41',
            'bg-green':'42',
            'bg-yellow':'43',
            'bg-blue':'44',
            'bg-magenta':'45',
            'bg-cyan':'46',
            'bg-white':'47',
        
        }

        def copts(options):
            pts=[]
            for opt in options.split(',') if options is not None else {}:
                nopt=mmap.get(opt.strip())
                if nopt:
                    pts.append(nopt)

            return pts

        def cstart(options):
            print '\033['+';'.join(copts(options))+'m'

        def cend():
            print '\033[0m'

        def cstr(val,options=None):
            return '\033['+';'.join(copts(options))+'m'+str(val)+'\033[0m'

        class XJCmd(cmd.Cmd):
            prompt='[ xj ] '

            def cmdloop(self,*args):
                try:
                    cmd.Cmd.cmdloop(self,*args)
                except KeyboardInterrupt as e:
                    self.cmdloop(*args)


            def do_EOF(self, *args):
                '''
                type <Ctrl>+D as a shortcut of command quit
                '''
                return self.do_quit(*args)

            def default(self, line):
                if line.startswith('$'):
                    global z
                    try:
                        cstart('bold,cyan')
                        cnt=0
                        trs=eval(line[:].replace('$','z'),{"z":z,"regex":regex,"within":within})
                        if isinstance(trs,str) or isinstance(trs,unicode):
                            print trs
                        else:
                            for ritem in trs:
                                cnt+=1
                                if isinstance(ritem,tuple):
                                    print '\t'.join([json.dumps(x) for x in ritem])
                                else:
                                    print ritem #json.dumps(ritem)

                            print>>sys.stderr,'='*10
                            print>>sys.stderr,cnt,'results returned'
                    except Exception as e:
                        print>>sys.stderr,'Invalid selector:',line[1:]
                        print>>sys.stderr, e
                    cend()

            def do_load(self, fname):
                try:
                    with open(fname) as fin:
                        global jo,z
                        jo=json.load(fin)
                        z=xj(jo)
                        print "Successfully Loaded ",fname
                        print ""
                except Exception as e:
                    print "Fail to load: ",fname
                    print e
                    print ""

            def do_quit(self,*arg):
                '''
                Never say Good-Bye!!
                '''
                print 'Bye!'
                print ""
                return True

            def do_loads(self,jsz):
                try:
                    global jo,z
                    jo=json.loads(jsz)
                    z=xj(jo)
                    print "Successfully Loaded from String"
                    print ""
                except Exception as e:
                    print "Fail to load from String"
                    print e
                    print ""

            def do_check(self,limit):
                global jo,z
                if jo is None:
                    print jo
                else:
                    if not limit:
                        rlimit=100
                    else:
                        rlimit=int(limit)
                    fsz=json.dumps(jo)
                    if len(fsz)<=rlimit or rlimit<=0:
                        print fsz
                    else:
                        print fsz[:rlimit/2],cstr('...','blue,bold,blink'),fsz[-rlimit/2:] 

                print ""

            def complete_path_track(self, text, line, begidx, endidx):
                clist= ['1','0','true','false','True','False','on','off']
                mline = line.partition(' ')[2]
                offs = len(mline) - len(text)
                return [s[offs:] for s in clist if s.startswith(mline)]
                
            def do_path_track(self,opt):
                global z

                if opt=='':
                    print cstr("path tracker",'bold,blue'),'is',cstr('on' if z.path_mode else 'off','red')

                else:
                    if opt.lower() in ['1','true','on']:
                        z.path_mode=True
                    elif opt.lower() in ['0','false','off']:
                        z.path_mode=False
                    else:
                        print "Unknown option: ",opt
                    print cstr("path tracker",'bold,blue'),'is',cstr('on' if z.path_mode else 'off','red')


        xcmd=XJCmd()
        xcmd.cmdloop('eXtended Json Command Line Interface')

    else:
        if options.sel is None:
            raise Exception('-s is not specified')

        opt=options.opts.strip()
        if opt not in ['value','path','values','paths','all'] and not opt.startswith('cc'):
            raise Exception("-o value|values|path|paths|all|cc[][]...|cc0[][]...")

        fin=open(options.ffile) if options.ffile is not None else sys.stdin
        
        for jsz in fin if options.byline else [fin.read()]:
            jo=json.loads(jsz)
            z=xj(jo)
            rs=eval('z'+options.sel,{'z':z,"regex":regex,'within':within})
            #print rs.paths
            #print rs.values
            if not opt.startswith('cc'):
                rsv=rs.__getattribute__(opt
                                        +('s' if opt in ['value','path'] else '')
                                    )
                print json.dumps( ((rsv[:1]+[""])[0] if opt in ['value','path'] else rsv) )
            else:
                for ln in eval(opt,{'cc0':rs.cc,'regex':regex,'within':within} if opt.startswith('cc0') else {'cc':rs.cc,'regex':regex,'within':within} ):
                    print json.dumps(ln)
                    if opt.startswith('cc0'):
                        break


    
if __name__=='__main__':
    from optparse import OptionParser
    parser = OptionParser()

    parser.add_option("--cli", action="store_true",dest="cli_mode", help="CLI mode")

    parser.add_option("--byline",action="store_true",dest="byline",help="load json by line from input")

    parser.add_option("-f", action="store", dest="ffile", help="load json from", default=None)

    parser.add_option("-s", action="store",dest="sel",help="select",default=None)

    parser.add_option("-o", action="store",dest="opts",help="options",default="values")
    
    # parser.add_option("-m", action="store",dest="rmode",help="result mode",default="value")
    (options, args) = parser.parse_args()

    main()
