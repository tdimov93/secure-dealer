
import os
import argparse
import gnupg
import random
import sys
from distutils.dir_util import copy_tree, remove_tree
from utils import read_json, read_file, write_json, write_file

PGP_HOME = 'pgphome'

DEFAULT_INPUTFILE = 'input.json'
DEFAULT_OUTDIR = 'output'

DATA_TEMPLATE = '{}\n================\nName: {}\nPassword: {}\n'


def import_admin_keys(gpg, indir, admins):
    fingerprints = []
    for admin in admins:
        key = read_file(os.path.join(indir, admin.get('keyfile')))
        import_result = gpg.import_keys(key)
        if import_result.count < 1:
            print('could not import admin key for {}'.format(admin.get('name')))
            continue

        fingerprints.append(import_result.fingerprints[0])
        print('Imported admin key for {}, fingerprint: {}'.format(admin.get('name'), import_result.fingerprints[0]))
    return fingerprints


def encrypt_data(gpg, name, assigned_name, generated_password, recipients):
    raw_data = DATA_TEMPLATE.format(name, assigned_name, generated_password)
    encrypted_data = gpg.encrypt(raw_data, recipients, always_trust=True)
    encrypted_str = str(encrypted_data)
    return encrypted_str


def randomize(config, indir, outdir):
    gpg = gnupg.GPG(gnupghome=PGP_HOME)

    entries = config.get('players')
    pool = config.get('pool')
    admins = config.get('admins')

    output = {}
    failed_entries = []
    admin_fingerprints = import_admin_keys(gpg, indir, admins)

    for entry in entries:
        # import key
        key = read_file(os.path.join(indir, entry.get('keyfile')))
        import_result = gpg.import_keys(key)
        if import_result.count < 1:
            failed_entries.append(entry.get('name'))
            continue
        fingerprint = import_result.fingerprints[0]
        print('Imported {} keys, fingerprint: {}'.format(import_result.count, import_result.fingerprints))

        # assign
        assigned_name = random.choice(pool)  # pick a name from the remaining pool at random
        pool.remove(assigned_name)  # remove the picked name from the pool

        # encrypt
        encrypted_str = encrypt_data(gpg, entry.get('name'), assigned_name, None, admin_fingerprints + [fingerprint])
        outfile = entry.get('keyfile').split('.')[0] + '.gpg'
        output[entry.get('name')] = {
            'fingerprint': fingerprint,
            'encrypted_data': outfile
        }
        write_file(os.path.join(outdir, outfile), encrypted_str)

    write_json(os.path.join(outdir, 'output.json'), output)
    if failed_entries:
        print('some of the entries could not be handled: {}'.format(failed_entries))
    else:
        print('successfully assigned and encrypted all entries')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='c', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('indir', type=str, help='Input directory containing a configuration file and the public keys of all entries stored in separate files')
    parser.add_argument('-c', '--config-file', type=str, default=DEFAULT_INPUTFILE, help='Name of the input configuration file inside the input directory', dest='configfile')
    parser.add_argument('-o', '--output', type=str, default=DEFAULT_OUTDIR, help='Output directory where the generated files will be stored. If it does not exist, the program will create it', dest='outdir')
    parser.add_argument('-b', '--backup', type=str, help='Name of a backup directory for previously generated files in case the specified output directory is not empty. Note: the program will not overwrite any existing data if no backup directory is specified.', dest='backup')

    args = parser.parse_args()

    if not os.path.isdir(args.indir):
        print('Specified input directory [{}] does not exist'.format(args.indir))
        sys.exit(1)
    if not os.path.isfile(os.path.join(args.indir, args.configfile)):
        print('Specified input directory [{}] does not contain an input.json configuration file'.format(args.indir))
        sys.exit(1)
    if not os.path.isdir(args.outdir):
        os.mkdir(args.outdir)
    if os.listdir(args.outdir) and not args.backup:
        print('Output directory is not empty, aborting. Consider using the -b option to tell the program where to backup any existing data for you.')
        sys.exit(0)
    elif os.listdir(args.outdir):  # and args.backup
        print('Output directory is not empty, backing up to {}'.format(args.backup))
        os.mkdir(args.backup)
        copy_tree(args.outdir, args.backup)
        remove_tree(args.outdir, verbose=1)
        os.mkdir(args.outdir)
    if not os.path.isdir(PGP_HOME):
        os.mkdir(PGP_HOME)

    config = read_json(os.path.join(args.indir, args.configfile))
    randomize(config, args.indir, args.outdir)
