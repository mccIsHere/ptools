import subprocess
import sys

class VWD(object):
    d_cmd_arr='vw -t -d /dev/stdin -p /dev/null --quiet -a -i %MOD%'.split()
    #dummy_eg='1.0 1.0 dummy|'
    
    verbose=False

    mod=property(lambda o:o._mod)
    c_scr=property(lambda o:o._c_scr)
    
    _sproc=None

    def __init__(self,mod_path):
        self._mod=mod_path
        self.cmd_arr=VWD.d_cmd_arr[:]
        self.cmd_arr[-1]=self.mod
        #self._c_scr=self.get_vw_score(VWD.dummy_eg)

    def set_vw_path(self,vw_path):
        self.cmd_arr[0]=vw_path

    def _getSProc(self):
        if self._sproc is None:
            cmdarr=self.cmd_arr #VWD.cmd.replace("%MOD%", self.mod).split()
            print>>sys.stderr, cmdarr
            self._sproc=subprocess.Popen(cmdarr,stdin=subprocess.PIPE,stderr=subprocess.STDOUT, stdout=subprocess.PIPE)

        return self._sproc

    def get_vw_score(self,vweg):
        sp=self._getSProc()
        sp.stdin.write(vweg.strip()+"\n")

        sln=sp.stdout.readline()
        dln=sp.stdout.readline()
        
        try:
            scr=float(sln.strip().split()[0])
            xarr=sorted([x for x in self.pgen(dln.strip().split("\t"))],key=lambda o:o["score"])
        except Exception as e:
            print>>sys.stderr,e,'[sln]',sln,'[dln]',dln
            raise Exception('expected')

        return {"score":scr,"detail":xarr}
    
    def pgen(self,oarr):
        for pt in oarr:
            if pt:
                fname,hid,ws,ss=pt.split(':')
                w=float(ws)
                s=float(ss)
                co={"name":fname,"hash":int(hid),"score":s}
                if w!=1.0:
                    co["weight"]=w
                if self.verbose or s!=0:
                    yield co

if __name__=='__main__':
    import sys,json

    mod=sys.argv[1]
    vwd=VWD(mod)
    for line in sys.stdin:
        scrobj=vwd.get_vw_score(line.strip())
        print scrobj["score"]
        print json.dumps(scrobj)

