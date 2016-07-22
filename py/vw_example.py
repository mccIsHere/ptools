import urllib,re

# refer to https://github.com/JohnLangford/vowpal_wabbit/wiki/Input-format



class VWFormater(object):
    ns_arr=None

    etype="logistic"
    accuracy=4

    _re_space = re.compile(r'\s+')
    _re_colon = re.compile(r':')
    _re_bar   = re.compile(r'\|')
    _re_apostrophe = re.compile(r"'")


    def __init__(self, ns_array, etype="logistic"):
        self.etype=etype
        if ns_array is not None:
            self.ns_arr=ns_array[:]

    def valid_label(self, label):
        if self.etype=="logistic":
            rlb=int(label)
            if rlb in [-1,1]:
                return str(rlb)
            else:
                raise Exception("Invalid label for "+self.etype+" : "+str(label))
        else:
            raise Exception("Unknown example type: "+self.etype)

    def valid_weight(self,weight,bHide=True):
        rwt=float(weight)
        if bHide and rwt==1.0:
            return None
        if rwt==0:
            return 0
        return format(rwt,'.'+str(self.accuracy)+'f')

    def valid_tag(self,tag,pref=""):
        # basically no char in [\\s,':','|']
        # also insert Q to the beginning, avoiding special vw cmd
        # return pref+urllib.quote(tag)
        tag_norm = tag
        tag_norm = VWFormater._re_space.sub('$SPA$', tag_norm)
        tag_norm = VWFormater._re_colon.sub('$COL$', tag_norm)
        tag_norm = VWFormater._re_bar.sub('$BAR$', tag_norm)
        tag_norm = VWFormater._re_apostrophe.sub('$APO$', tag_norm)

        return pref+tag_norm

    def fw_pair(self,feat,weight):
        rt=self.valid_tag(feat)
        rw=self.valid_weight(weight)
        if rw is not None:
            if rw==0:
                return None
            else:
                return rt+':'+rw
        else:
            return rt

    def format(self,label,weight,tag,feat_map,ns_weights):
        rlb=self.valid_label(label)

        rwt=self.valid_weight(weight,False)
        rtag=self.valid_tag(tag,"Q")

        rs=rlb+' '+rwt+' '+rtag

        ns_seq=self.ns_arr or sorted(feat_map.keys())

        if not ns_seq:
            return None

        for ns in ns_seq:
            nspt='|'+self.fw_pair(ns, (ns_weights or {}).get(ns,1.0) )+' '

            for feat in feat_map.get(ns,{}):
                cpair=self.fw_pair(feat,feat_map[ns][feat])
                if cpair is not None:
                    nspt+=cpair+' '

            rs+=nspt

        return rs
