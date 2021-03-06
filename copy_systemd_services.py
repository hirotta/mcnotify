import sys
import os
import errno
import shutil
import configparser

def ask_dirpath(prompt, default, check_existence = True):
    prompt = '{0} (default: {1}) :'.format(prompt, default)
    res = input(prompt)

    if len(res) == 0:
        return default

    if check_existence:
        path = os.path.abspath(res)
        if os.path.exists(path) and os.path.isdir(path):
            return path
        else:
            return None
    else:
        return res

def ask_overwrite(path):
    if os.path.exists(path):
        answer = input('{0} already exists! overwrite? (y/n): '.format(path))
        if answer[0] == 'y':
            return True
        else:
            return False
    else:
        return True


def main():
    print('=== systemd services installation ===')
    print('answer questions below.')
    print('')

    # ask mcnotify path
    default = os.getcwd()
    prompt = 'Path to mcnotify directory'
    while True:
        mcnotify_path = ask_dirpath(prompt, default)
        if mcnotify_path == None:
            sys.stdout.write('!!! {0} doesn\'t exist.\n'.format(path))
            continue
        else:
            break

    # copy destination
    default = '{0}/.config/systemd/user/'.format(os.environ['HOME'])
    prompt = 'Path to systemd directory'
    systemd_path = ask_dirpath(prompt, default)

    # install
    ## mkdir
    try:
        os.mkdir(systemd_path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(systemd_path):
            pass
        else:
            raise e

    services_path = '{0}/{1}'.format(mcnotify_path, 'systemd_services')

    ## service file
    service_basename = 'mcnotify.service'
    service_path = '{0}/{1}'.format(services_path, service_basename)
    service_destination_path = os.path.abspath('{0}/{1}'.format(systemd_path, service_basename))

    print('installing {0}...'.format(service_basename))
    ### check existence and make service file
    if os.path.exists(service_path):
        service = configparser.ConfigParser()
        service.optionxform = str
        service.read(service_path)
        service['Service']['WorkingDirectory'] = mcnotify_path
    else:
        sys.stdout.write('!!! {0} doesn\'t exist. You specified wrong basepath?\n'.format(service_path))
        sys.exit(1)

    ### install service file
    if ask_overwrite(service_destination_path):
        with open(service_destination_path, 'w+') as servicefile:
            service.write(servicefile)
    else:
        sys.stderr.write('!!! {0} must be overwritten.\n'.format(service_destination_path))
        sys.exit(1)

    ## timer file
    timer_basename = 'mcnotify.timer'
    timer_path = '{0}/{1}'.format(services_path, timer_basename)
    timer_destination_path = os.path.abspath('{0}/{1}'.format(systemd_path, timer_basename))

    print('installing {0}...'.format(timer_basename))
    ### check existence
    if not os.path.exists(timer_path):
        sys.stdout.write('!!! {0} doesn\'t exist. You specified wrong basepath?\n'.format(timer_path))
        sys.exit(1)

    ### install timer file
    if ask_overwrite(timer_destination_path):
        shutil.copyfile(timer_path, timer_destination_path)
    else:
        sys.stderr.write('!!! {0} must be overwritten.\n'.format(service_destination_path))
        sys.exit(1)

main()
