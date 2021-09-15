import toml


conf = toml.load("sqconfig.toml")


def write_conf():
    toml.dump(conf, open("sqconfig.toml", "w"))
