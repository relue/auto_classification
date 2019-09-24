import collections
import json

def get_config(conf_d, conf_name):
    default_conf_fp = "auto_classification/conf/"+conf_name+"_default.json"
    default_conf = load_json(default_conf_fp)
    upd_conf = update(default_conf,conf_d)
    return upd_conf

def load_json(fp):
    with open(fp) as json_data:
        json_d = json.load(json_data)
    return json_d

def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d
