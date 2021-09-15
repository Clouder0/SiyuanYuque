import toml


conf = toml.load("config.toml")


def write_conf():
    toml.dump(conf, open("config.toml", "w"))
