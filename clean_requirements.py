import re

# System-level packages to exclude from pip installs
banned_keywords = [
    'cloud-init',
    'command-not-found',
    'python-apt',
    'ubuntu-pro-client',
    'ubuntu-advantage-tools',
    'libgirepository',
    'libsystemd',
    'python-dateutil==2.9.0',  # invalid version
    'python-dbus',
    'python3-software-properties',
    'python3-update-manager',
    'python3-gi',
    'gobject',
    'systemd-python',
    'python-debian',
]

def is_valid_line(line):
    line = line.strip()
    if not line or line.startswith('#'):
        return True
    return not any(pkg in line for pkg in banned_keywords)

def clean_requirements_file(filename='requirements.txt'):
    with open(filename, 'r') as file:
        lines = file.readlines()

    cleaned_lines = [line for line in lines if is_valid_line(line)]

    with open(filename, 'w') as file:
        file.writelines(cleaned_lines)

    print(f"✅ Cleaned {filename}: Removed {len(lines) - len(cleaned_lines)} invalid lines.")

if __name__ == "__main__":
    clean_requirements_file()

