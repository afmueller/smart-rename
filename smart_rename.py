from collections import namedtuple as ntup
import os
from cement import App, CaughtSignal, Controller, get_version
import ngrams

VERSION = (0, 0, 1, 'alpha', 0)

VERSION_BANNER = """
smartrename v%s
""" % get_version()


class Renamer():
    
    lower_list = ["a", "an", "the", "and", "but", "or", "for", "nor", "with", 
                  "to", "on", "as", "at", "by", "in", "of", "mid", "off", 
                  "per", "qua", "re", "up", "via", "o'", "'n'", "n'"]
    
    def suggest_correction(self, filepath):
        filename = os.path.basename(filepath)
        filename, ext = os.path.splitext(filename)
        
        result_segments = []
        # Process each segment individually
        for token in filename.split('_'):
            prob, words = ngrams.segment2(token)
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
            (['files'],
              { 'action' : 'store',
                'nargs'  : '+'} )
        ]


    def _default(self):
        """Default action if no sub-command is passed."""
        print("Start processing files")
        print("")
        r = Renamer()
        T = ntup('T', ['path', 'suggestion', 'correction'])

        # Get list of paths
        path_list = self.app.pargs.files
        
        # Repeat steps until satisfied with corrections
        suggestions_accepted = False
        while not suggestions_accepted:
            # 1. Configure algorithm (or use defaults, if nothing specified)
            if False:
                print("Configuring algorithm")
        
            # 2. Get suggestions for new names
            suggestions = [T(p, r.suggest_correction(p), '') for p in path_list]
        
            # 3. Display suggestions
            for (path_orig, path_sugg, path_corr) in suggestions:
                print("Renaming {}:".format(path_orig))
                print("  -> {}".format(path_corr if path_corr else path_sugg))
        
            # 4. Display prompt and ask for suggestions
            print("")
            print("Proceed with suggestions? y/a/e/l/? [y]")
            answer = input().strip().lower()
            if (answer == "a"):
                return
            elif (answer == "e"):
                raise NotImplementedError()
            elif (answer == "l"):
                raise NotImplementedError()
            elif (answer == "y" | answer == ""):
                suggestions_accepted = True
        
        # When satisfied with results, rename files
        print("Renaming files...")
    


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
