
import os
import argparse
import gnupg
import random
import sys
from distutils.dir_util import copy_tree, remove_tree
from utils import read_json, read_file, write_json, write_file


class SecureDealer():

    PGP_HOME = 'pgphome'

    DEFAULT_INPUTFILE = 'input.json'
    DEFAULT_PEEKFILE = 'output.json'
    DEFAULT_OUTDIR = 'output'

    DATA_TEMPLATE = '{}\n================\nName: {}\nPassword: {}\n'

    def __init__(self):
        if not os.path.isdir(SecureDealer.PGP_HOME):
            os.mkdir(SecureDealer.PGP_HOME)

        self.config = None
        self.input_dir = None
        self.output_dir = None
        self.gpg = gnupg.GPG(gnupghome=SecureDealer.PGP_HOME)

        parser = argparse.ArgumentParser(
            description='The secure dealer assigns/deals each player a randomly picked element from a pre-defined pool and creates 1 PGP-encrypted file per player containing data that can only be decrypted by the player\'s public key (and any specified master keys)',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            usage='''secure-dealer <command> [<args>]

The most commonly used commands are:
   deal    Distribute a randomly picked element from the deck/pool to each player
   peek    Peek at what was dealt. The output is encrypted by default unless proper credentials are specified
''')
        parser.add_argument('command', type=str, help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Command not supported: {}'.format(args.command))
            parser.print_help()
            sys.exit(1)
        getattr(self, args.command)()

    def deal(self):
        parser = argparse.ArgumentParser(description='Distribute a randomly picked element from the deck/pool to each player', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('indir', type=str, help='Input directory containing a configuration file and the public keys of all entries stored in separate files')
        parser.add_argument('-c', '--config-file', type=str, default=SecureDealer.DEFAULT_INPUTFILE, help='Name of the input configuration file inside the input directory', dest='config_file')
        parser.add_argument('-o', '--output', type=str, default=SecureDealer.DEFAULT_OUTDIR, help='Output directory where the generated files will be stored. If it does not exist, the program will create it', dest='outdir')
        parser.add_argument('-b', '--backup', type=str, help='Name of a backup directory for previously generated files in case the specified output directory is not empty. Note: the program will not overwrite any existing data if no backup directory is specified.', dest='backup')

        args = parser.parse_args(sys.argv[2:])

        self.handle_indir_args(args)
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

        self.input_dir = args.indir
        self.output_dir = args.outdir
        self.config = read_json(os.path.join(args.indir, args.config_file))
        self.shuffle()

    def peek(self):
        parser = argparse.ArgumentParser(description='Take a peek at what was dealt. The output is encrypted by default unless proper credentials are specified', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('indir', type=str, help='Input directory containing previously generated data - this will typically be the output of a deal command')
        parser.add_argument('-c', '--config-file', type=str, default=SecureDealer.DEFAULT_PEEKFILE, help='Name of the input configuration file inside the input directory', dest='config_file')

        args = parser.parse_args(sys.argv[2:])
        self.handle_indir_args(args)

    def handle_indir_args(self, args):
        if not os.path.isdir(args.indir):
            print('Specified input directory [{}] does not exist'.format(args.indir))
            sys.exit(1)
        if not os.path.isfile(os.path.join(args.indir, args.config_file)):
            print('Specified input directory [{}] does not contain a JSON configuration file [{}]'.format(args.indir, args.config_file))
            sys.exit(1)

    def import_admin_keys(self, admins):
        fingerprints = []
        for admin in admins:
            key = read_file(os.path.join(self.input_dir, admin.get('keyfile')))
            import_result = self.gpg.import_keys(key)
            if import_result.count < 1:
                print('could not import admin key for {}'.format(admin.get('name')))
                continue

            fingerprints.append(import_result.fingerprints[0])
            print('Imported admin key for {}, fingerprint: {}'.format(admin.get('name'), import_result.fingerprints[0]))
        return fingerprints

    def encrypt_data(self, name, assigned_name, generated_password, recipients):
        raw_data = SecureDealer.DATA_TEMPLATE.format(name, assigned_name, generated_password)
        encrypted_data = self.gpg.encrypt(raw_data, recipients, always_trust=True)
        encrypted_str = str(encrypted_data)
        return encrypted_str

    def shuffle(self):
        players = self.config.get('players')
        pool = self.config.get('pool')
        admins = self.config.get('admins')

        output = {}
        failed_players = []
        admin_fingerprints = self.import_admin_keys(admins)

        for player in players:
            # import key
            key = read_file(os.path.join(self.input_dir, player.get('keyfile')))
            import_result = self.gpg.import_keys(key)
            if import_result.count < 1:
                failed_players.append(player.get('name'))
                continue
            fingerprint = import_result.fingerprints[0]
            print('Imported {} keys, fingerprint: {}'.format(import_result.count, import_result.fingerprints))

            # assign
            assigned_name = random.choice(pool)  # pick a name from the remaining pool at random
            pool.remove(assigned_name)  # remove the picked name from the pool

            # encrypt
            encrypted_str = self.encrypt_data(player.get('name'), assigned_name, None, admin_fingerprints + [fingerprint])
            outfile = player.get('keyfile').split('.')[0] + '.gpg'
            output[player.get('name')] = {
                'fingerprint': fingerprint,
                'encrypted_data': outfile
            }
            write_file(os.path.join(self.output_dir, outfile), encrypted_str)

        write_json(os.path.join(self.output_dir, 'output.json'), output)
        if failed_players:
            print('some of the players could not be handled: {}'.format(failed_players))
        else:
            print('successfully assigned and encrypted all players')


if __name__ == "__main__":
    SecureDealer()
