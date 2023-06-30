def config_parser(config_path):
    with open(config_path, "r") as config_file:
        config = dict()
        lines = config_file.readlines()
        for i in lines:
            k, y = i.split(" = ")
            config[k] = y.split()[0]
        return config