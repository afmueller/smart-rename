import json
import os
import re

from cement import App, CaughtSignal, Controller, get_version
from cement.utils.misc import init_defaults
from num2words import num2words

from segmenter import Segmenter


VERSION = (0, 0, 1, 'alpha', 0)

VERSION_BANNER = """
smartrename v%s
""" % get_version()


# configuration defaults
CONFIG = init_defaults('smartrename', 'segmenter')
CONFIG['segmenter']['ngrams_file'] = 'ngrams.json'


class Renamer():
    
    lower_list = ["a", "an", "the", "and", "but", "or", "for", "nor", "with", 
                  "to", "on", "as", "at", "by", "in", "of", "mid", "off", 
                  "per", "qua", "re", "up", "via", "o'", "'n'", "n'"]
    
    def __init__(self, app, config = None):
        
        self.app = app
        
        ngrams_file = config.get('segmenter', 'ngrams_file')
        self.app.log.debug(f'Trying to load ngrams file {ngrams_file}')
        try:
            with open(ngrams_file, 'r') as nf:
                ngrams = json.load(nf)
                self.app.log.debug(f'Loaded ngrams file {ngrams_file}.')
        except FileNotFoundError as err:
            self.app.log.info(f'Ngrams file {ngrams_file} not found. Using default configuration.')

        self._ws = Segmenter(ngrams)
    
    def suggest_correction(self, filepath):
        filename = os.path.basename(filepath)
        filename, ext = os.path.splitext(filename)
        
        # Look for ending '2e', '3e' etc giving edition number
        edition_match = re.match('(.*)(\d)e$', filename)
        filename, edition = edition_match.groups() if edition_match else (filename, '')
        
        result_segments = []
        # Process each segment individually
        for token in filename.split('_'):
            words = self._ws.segment(token)
            # To title case
            words = [
                    words[0][:1].upper() + words[0][1:]
            ] + [
                    (word[:1].upper() if word not in self.lower_list else word[:1]) 
                    + word[1:] for word in words[1:]
            ]
            result_segments.append(' '.join(words))

        # Join suggestions for segments
        result = " - ".join(result_segments)
        # Add edition information
        if edition:
            result = result + ' ({} edition)'.format(num2words(edition, to='ordinal_num'))
        return result + ext


class Base(Controller):
    class Meta:
        label = 'base'

        arguments = [
            ### add a version banner
            ( [ '-v', '--version' ],
              { 'action'  : 'version',
                'version' : VERSION_BANNER } ),
            ( ['files'],
              { 'action' : 'store',
                'nargs'  : '+'} )
        ]


    def _default(self):
        """Default action if no sub-command is passed."""

        # Initialize classes
        print('Initializing')
        config = self.app.config
        r = Renamer(self.app, config)

        # Startup        
        print('Start processing files', os.linesep)

        # Get list of paths
        path_list = self.app.pargs.files
        
        # Repeat steps until satisfied with corrections
        suggestions_accepted = False
        while not suggestions_accepted:
            # 1. Configure algorithm (or use defaults, if nothing specified)
            if False:
                print('Configuring algorithm')
        
            # 2. Get suggestions for new names
            suggestions = [{'path': p, 'suggestion': r.suggest_correction(p)} for p in path_list]
        
            # 3. Display suggestions
            for entry in suggestions:
                print('Renaming {}:'.format(entry['path']))
                print('  -> {}'.format( entry['correction'] if 'correction'in entry
                                        else entry['suggestion']))
        
            # 4. Display prompt and ask for suggestions
            print()
            print('Proceed with suggestions? y/a/e/l/? [y]')
            answer = input().strip().lower()
            if (answer == 'a'):
                # abort
                return
            elif (answer == 'e'):
                # edit suggestions
                raise NotImplementedError()
            elif (answer == 'l'):
                # switch language
                raise NotImplementedError()
            elif (answer == '?'):
                # print help
                print_help()
            elif ((answer == 'y') or (answer == '')):
                # default option: accept suggestions
                suggestions_accepted = True
        
        # When satisfied with results, rename files
        print('Renaming files. . .', end='')
        for entry in suggestions:
            fn = entry['path']
            new_name = entry['correction'] if 'correction' in entry else entry['suggestion']
            directory = os.path.split(fn)[0]
            os.rename(fn, os.path.join(directory, new_name))
        print('done.')


def print_help():
    print('Available options:')
    print('y - Accept suggestions')
    print('a - Abort')
    print('e - Edit suggestions')
    print('l - Switch language')
    print('? - Print help')
    print()


class MyApp(App):

    class Meta:
        # application label
        label = 'smartrename'
        
        # initialize application defaults
        extensions = [
            'yaml',
        ]
        config_defaults = CONFIG
        config_handler = 'yaml'
        config_files = [
                './smartrename.yml'
        ]

        # register handlers
        handlers = [
            Base
        ]

        # call sys.exit() on close
        close_on_exit = True


def main():
    with MyApp() as app:
        try:
            app.run()
        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('\n%s' % e)
            app.exit_code = 0


if __name__ == '__main__':
    main()
