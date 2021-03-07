from collections import namedtuple as ntup
import os

from cement import App, CaughtSignal, Controller, get_version
import hcl2

from segmenter import Segmenter


VERSION = (0, 0, 1, 'alpha', 0)

VERSION_BANNER = """
smartrename v%s
""" % get_version()


class Renamer():
    
    lower_list = ["a", "an", "the", "and", "but", "or", "for", "nor", "with", 
                  "to", "on", "as", "at", "by", "in", "of", "mid", "off", 
                  "per", "qua", "re", "up", "via", "o'", "'n'", "n'"]
    
    def __init__(self, config = None):
        
        self._ws = Segmenter()
        
        #TODO: Get unigrams and bigrams from config object (unigrams and bigrams coming from different files)
        print(type(config))
    
    def suggest_correction(self, filepath):
        filename = os.path.basename(filepath)
        filename, ext = os.path.splitext(filename)
        
        result_segments = []
        # Process each segment individually
        for token in filename.split('_'):
            print(token)
            words = self._ws.segment(token)
            # To title case
            words = [
                    words[0][:1].upper() + words[0][1:]
            ] + [
                    (word[:1].upper() if word not in self.lower_list else word[:1]) 
                    + word[1:] for word in words[1:]
            ]
            result_segments.append(' '.join(words))

        return " - ".join(result_segments) + ext


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
        config = {}
        self.app.log.debug('trying to load config file')
        try:
            with open('config.hcl', 'r') as cf:
                config = hcl2.load(cf)
                self.app.log.debug('loaded config file config.hcl.')
        except FileNotFoundError as err:
            self.app.log.info('config file config.hcl not found. Using default configuration.')

        r = Renamer(config)

        # Startup        
        print('Start processing files', os.linesep)
        # Define namedtuple for storing suggestions
        T = ntup('T', ['path', 'suggestion', 'correction'])

        # Get list of paths
        path_list = self.app.pargs.files
        
        # Repeat steps until satisfied with corrections
        suggestions_accepted = False
        while not suggestions_accepted:
            # 1. Configure algorithm (or use defaults, if nothing specified)
            if False:
                print('Configuring algorithm')
        
            # 2. Get suggestions for new names
            suggestions = [T(p, r.suggest_correction(p), '') for p in path_list]
        
            # 3. Display suggestions
            for (path_orig, path_sugg, path_corr) in suggestions:
                print('Renaming {}:'.format(path_orig))
                print('  -> {}'.format(path_corr if path_corr else path_sugg))
        
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
                raise NotImplementedError()
            elif (answer == 'y' | answer == ''):
                # default option: accept suggestions
                suggestions_accepted = True
        
        # When satisfied with results, rename files
        print('Renaming files...')
    


class MyApp(App):

    class Meta:
        # application label
        label = 'smartrename'

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
