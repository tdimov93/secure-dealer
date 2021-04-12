
import json


def read_json(filename):
    try:
        with open(filename, 'r') as infile:
            array = json.load(infile)
        return array
    except Exception as ex:
        print('oops, could not read json file {}'.format(filename))
    return None


def write_json(filename, data):
    try:
        with open(filename, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=False)
    except Exception as ex:
        print('oops, could not write json file {}'.format(filename))


def read_file(filename):
    try:
        with open(filename, 'r') as infile:
            return infile.read()
    except Exception as ex:
        print('oops, could not read file {}'.format(filename))
    return None


def write_file(filename, data):
    try:
        with open(filename, 'w+') as outfile:
            outfile.write(data)
    except Exception as ex:
        print('oops, could not write file {}'.format(filename))


def format_json(data, indent=4):
    return json.dumps(data, indent=indent, sort_keys=False)


def print_json(data, indent=4, print_fct=print):
    print_fct(format_json(data, indent))
