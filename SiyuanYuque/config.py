import toml
from siyuanhelper import helper as siyuan


conf = toml.load("sqconfig.toml")
siyuan.set_token(conf["siyuan_token"])


def write_conf():
    toml.dump(conf, open("sqconfig.toml", "w"))
