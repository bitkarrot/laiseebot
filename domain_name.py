import yaml

path  = "./"
config_file = path + 'config.yml'

def get_domain():
    with open(config_file, 'rb') as f:
        config = yaml.safe_load(f)
        domain = config['domain_name']
    f.close()
    return domain

if __name__ == '__main__':
    name = get_domain()
    print(name)
