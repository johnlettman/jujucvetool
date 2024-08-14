
# TODO: WORK IN PROGRESS

import subprocess

cached_results = {}

def get_systemd_service_restarts(package_name):
    # Check if the results are cached
    if package_name in cached_results:
        return cached_results[package_name]

    # Download the package file
    subprocess.run(['apt-get', 'download', package_name])

    # Get the path to the downloaded package file
    package_path = subprocess.check_output(['apt-cache', 'show', package_name,
                                            '|', 'grep', 'Filename', '|', 'cut', '-d', ' ', '-f', '2'],
                                           shell=True).decode().strip()

    # Get the path to the package's post-installation script
    script_path = subprocess.check_output(['dpkg-deb', '-c', package_path, '|', 'grep', 'postinst', '|',
                                           'cut', '-d', ' ', '-f', '6'], shell=True).decode().strip()

    # Read the contents of the script
    with open(script_path, 'r') as f:
        script_content = f.read()

    # Search for systemd service restart commands in the script
    restart_commands = [line.split()[1] for line in script_content.splitlines()
                        if 'systemctl' in line and 'restart' in line]

    # Extract the service names from the restart commands
    service_names = [cmd.split('.')[0] for cmd in restart_commands]

    # Cache the results
    cached_results[package_name] = service_names

    return service_names

print(get_systemd_service_restarts("openssh-server"))
