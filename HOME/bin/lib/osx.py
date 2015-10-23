import abc
import getpass
import logging
import os
import pwd
import re
import shutil
import subprocess
from collections import OrderedDict
from distutils.util import strtobool

log = logging.getLogger(__name__)


def ensure_correct_usrlocal_permissions(*args, **kwargs):
    user = getpass.getuser()
    uid = os.stat('/usr/local').st_uid
    local_owner = pwd.getpwuid(uid).pw_name

    log.debug("Currently logged in user is {!r}, owner of /usr/local is {!r}".format(
        user, local_owner))

    if user != local_owner:
        log.info("Fixing permissions on /usr/local before running Homebrew")
        # stupid that there's a shutil.chown but no shutil.chown -R
        cmd = ['sudo', 'chown', '-R', user, '/usr/local']
        log.info("Executing command: {!r}".format(cmd))
        subprocess.check_call(cmd)


def brew(action, settings, *args, **kwargs):
    # ensure homebrew is installed
    if not shutil.which('brew'):  # hey look 'which' is built in as of Python 3.3
        # todo: install homebrew if not installed
        # http://brew.sh/
        # ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
        raise Exception("Homebrew must be installed")

    if kwargs.get('fix_repo', False):
        # http://stackoverflow.com/questions/14113427/brew-update-failed
        log.info("Fixing Homebrew repository")
        cmd = 'cd `brew --prefix`; git reset --hard origin/master'
        log.info("Executing command: {!r}".format(cmd))
        subprocess.check_call(cmd, shell=True)

    formulas = settings['homebrew']['formulas']

    # fix permissions on /usr/local if necessary
    ensure_correct_usrlocal_permissions()

    # ensure homebrew updated
    log.info("Running 'brew update'")
    subprocess.check_call(['brew', 'update'])

    # upgrade all existing packages
    log.info("Running 'brew upgrade'")
    subprocess.call(['brew', 'upgrade', '--all'])
    # ideally this would be check_call but homebrew returns an error code in cases that
    # aren't actually errors: https://github.com/Homebrew/homebrew/issues/27048
    # so, make sure to inspect the output for problems

    # ensure expected packages are installed
    log.info("Expected packages are: {}".format(', '.join(sorted(formulas))))
    # bytes.decode defaults to utf-8, which *should* also be the default system encoding
    # but I suppose to really do this correctly I should check that. However, pretty sure
    # all Homebrew package names should be ascii anyway so it's fine
    installed_packages = subprocess.check_output(['brew', 'list']).decode().split()
    log.info("Currently installed packages are: {}".format(', '.join(installed_packages)))

    # install missing packages
    missing_packages = sorted(set(formulas) - set(installed_packages))
    log.info("Missing packages are: {}".format(', '.join(missing_packages)))
    for p in missing_packages:
        log.info("Installing package: {}".format(p))
        subprocess.check_call(['brew', 'install', p])

    # run post-install operations
    post_install = settings['homebrew']['post_install']
    if post_install:
        log.info("Running post-install operations")

        for cmd in post_install:
            shell = isinstance(cmd, str)  # run with shell=True if the command is a string
            log.info("Running cmd (shell={!r}): {!r}".format(shell, cmd))
            subprocess.check_call(cmd, shell=shell)

    # clean up outdated packages
    log.info("Running 'brew cleanup'")
    subprocess.call(['brew', 'cleanup'])


class mybool(metaclass=abc.ABCMeta):
    """
    Provide something that will parse '0' as False
    because that's how 'defaults' returns false values

    """
    def __new__(self, value='0'):
        return bool(strtobool(value))

mybool.register(bool)


# map 'defaults' types to Python's types
# Use OrderedDict because isinstance(True, int) is True, so compare to bool first
DEFAULTS_TO_PYTHON_TYPE = OrderedDict((
    ('boolean', mybool),
    ('integer', int),
    ('float', float),
    ('string', str),
))


def defaults_read(domain, key, missing_ok=False):
    cmd = ['defaults', 'read-type', domain, key]
    log.debug("Executing command: {!r}".format(cmd))
    try:
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output.decode()  # bytes -> string
        log.warning("Error reading setting {}:{}. Return code {}, output was: {}".format(
            domain, key, e.returncode, output))

        if 'does not exist' in output:
            log.warning("Prior value for {}:{} doesn't exist".format(domain, key))
            if missing_ok:
                return None

        raise

    log.debug("Result was: {!r}".format(result))

    result_type = re.match('Type is (\w+)', result.decode()).group(1)
    type = DEFAULTS_TO_PYTHON_TYPE[result_type]

    cmd = ['defaults', 'read', domain, key]
    log.debug("Executing command: {!r}".format(cmd))
    result = subprocess.check_output(cmd)
    typed_result = type(result.decode().rstrip('\n'))
    log.debug("Result was: {!r}, typed_result was {!r}".format(result, typed_result))
    return typed_result


def defaults_write(domain, key, value):
    cmd = ['defaults', 'write', domain, key]

    for type_str, type in DEFAULTS_TO_PYTHON_TYPE.items():
        if isinstance(value, type):
            break
    else:
        raise Exception("Unsupported value type provided to defaults_write: {!r}".format(value))

    cmd.extend(['-{}'.format(type_str), str(value)])

    log.debug("Executing command: {!r}".format(cmd))
    subprocess.check_call(cmd)


def update_os_settings(settings):
    # useful resources
    # https://github.com/mathiasbynens/dotfiles/blob/master/.osx

    # defaults read | pbcopy to get a list of all current settings

    defaults = settings['osx']['defaults']
    for domain, settings in sorted(defaults.items()):
        for key, value in sorted(settings.items()):
            old_value = defaults_read(domain, key, missing_ok=True)

            if old_value != value:
                log.info("Setting new value for {}:{}. Old value: {!r}, new value: {!r}.".format(
                    domain, key, old_value, value))

            defaults_write(domain, key, value)


def restart_os_functions(*args, **kwargs):
    for item in ('Finder', 'Dock', 'SystemUIServer'):
        cmd = ['killall', item]
        log.info("Executing command: {!r}".format(cmd))
        subprocess.check_call(cmd)