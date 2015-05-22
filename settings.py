{
    'actions': {
        'status': {
            'func': 'repo',
            'cmd': ['status'],
            'help': 'Get repository status'
        },
        'diff': {
            'func': 'repo',
            'cmd': ['diff'],
            'help': 'Get repository diff'
        },
        'commit': {
            'func': 'repo',
            'cmd': ['commit', '-am', '{message}'],
            'args': {'message': {'help': 'The commit message'}},
            'help': 'Commit to repository'
        },
        'pull': {
            'func': 'repo',
            'cmd': ['pull'],
            'help': 'Pull repository from server',
            'aliases': ['update'],
        },
        'push': {
            'func': 'repo',
            'cmd': ['push'],
            'help': 'Push repository to server'
        },
        'brew': {
            'func': 'brew',
            # initial space because the beermug takes up two character spaces
            # and overlaps if you don't pad it with a space afterwards
            'help': "\U0001F37A Homebrew\U0001F37A"
        },
        'debug': {  # load the setup program as a module and start an interactive console
            'func': 'debug',
            'help': 'Start an interactive console'
        },
        'restart_os_functions': {
            # https://blog.cloudtroopers.com/how-restart-mac-os-x-finder-dock-or-menubar
            # this should be run if any settings change, but you don't necessarily
            # need to run this every time 'update_os_settings' is run
            'func': 'restart_os_functions',
            'help': 'Restart Finder, Menubar, Dock, etc.'
        }
    },
    'symlinks': {
        'overrides': {
            # overrides should not have slashes at the end even though it's a directory
            # because it refers to the symlink that's created
            'sublime_text': 'Library/Application Support/Sublime Text 3/Packages/User'
        },
        # 'ignores_file': '.gitignore_global',  # piggyback off of gitignore_global
        # this path should be resolved correctly because 'setup' sets the cwd
        # to the root of the repository
        'ignores': list(
            filter(
                # ignore comments, negations, and empty lines
                lambda line: not line.startswith(('#', '!')) and line,
                open('HOME/.gitignore_global').read().splitlines()
            )
        ),
    },
    'homebrew': {
        "formulas": [
            "jq",
            "meld"
        ]
    },
    'osx': {
        'defaults': {
            'com.apple.dock': {
                # http://www.defaults-write.com/enable-highlight-hover-effect-for-grid-view-stacks/
                'mouse-over-hilite-stack': True,

                # hot corners
                # Possible values:
                #  0: no-op
                #  2: Mission Control
                #  3: Show application windows
                #  4: Desktop
                #  5: Start screen saver
                #  6: Disable screen saver
                #  7: Dashboard
                # 10: Put display to sleep
                # 11: Launchpad
                # 12: Notification Center

                # bottom left: sleep
                'wvous-bl-corner': 10,
                'wvous-bl-modifier': 0,

                # top left: mission control
                'wvous-tl-corner': 2,
                'wvous-tl-modifier': 0,

                # top right: desktop
                'wvous-tr-corner': 4,
                'wvous-tr-modifier': 0,

                # bottom right: application windows
                'wvous-br-corner': 3,
                'wvous-br-modifier': 0,
            },
            'com.apple.finder': {
                'ShowPathbar': True,
                'ShowStatusBar': True,
            },
            "com.apple.menuextra.battery": {
                # the menubar widget actually sets 'YES' or 'NO' but bool values work too
                'ShowPercent': True,
            },
        }
    }
}