#!/usr/bin/python
import os
import re
import platform
import subprocess
import yaml
import distutils.spawn

# define some terminal colours to use
class bcolors:
  GOOD = '\033[92m'
  BAD = '\033[91m'
  RESET = '\033[0m'

# define some icons to use
print_tick = bcolors.GOOD + u"\u2713" + bcolors.RESET
print_cross = 	bcolors.BAD + u"\u2A2F" + bcolors.RESET

# define supported package managers
package_managers = ['yum', 'apt-get', 'pacman', 'emerge']
package_manager = "None"

# detect if an application with the provided name is installed
def is_installed(name):
  return distutils.spawn.find_executable(name) is not None

# check which package manager is installed
for manager in package_managers:
  if is_installed(manager):
    package_manager = manager

# load the manifest file in
with open('manifest.yml', 'r') as f:
  try:
    manifest = yaml.load(f)
  except:
    print "Invalid yaml file"
    exit(0)

print "loaded manifest"

to_install = []
unable_to_satisfy = []

# loop through the manifest setting up the environment
if manifest.has_key('dependancies'):
  print "Checking dependancies"
  if manifest['dependancies'].has_key('commands'):
    cmd = "where" if platform.system() == "Windows" else "which"
    for dependancy in manifest['dependancies']['commands']:
      if isinstance(dependancy, basestring):
        if is_installed(dependancy):
          print (print_tick + dependancy)
        else:
          print (print_cross + dependancy)
          FNULL = open(os.devnull, 'w')
          output = subprocess.Popen([package_manager, 'provides', dependancy], stdout=subprocess.PIPE, stderr=FNULL)
          provides = output.stdout.read()
          found_a_package_to_satisfy_dependancy = False
          for result in provides.split('\n'):
            if dependancy in result:
              package = result.split(' ')[0]
              to_install.append(package)
              found_a_package_to_satisfy_dependancy = True
          if found_a_package_to_satisfy_dependancy == False:
            unable_to_satisfy.append(dependancy)
    print "\r\n"
  if manifest['dependancies'].has_key(package_manager):
    for package in manifest['dependancies'][package_manager]:
      FNULL = open(os.devnull, 'w')
      output = subprocess.Popen([package_manager, 'list', package], stdout=subprocess.PIPE, stderr=FNULL)
      package_list = output.stdout.read()
      found_a_package_to_satisfy_request = False
      for result in package_list.split('\n'):
        if package in result:
          to_install.append(package.split('.')[0])
          found_a_package_to_satisfy_request = True
      if found_a_package_to_satisfy_request == False:
        unable_to_satisfy.append(package)

if len(to_install) > 0:
  print "Packages to install"
  for package in to_install:
    print bcolors.GOOD + package + bcolors.RESET
  print "\r\n"

if len(unable_to_satisfy) > 0:
  print "Unable to satisfy dependancies:"
  for application in unable_to_satisfy:
    print bcolors.BAD + application + bcolors.RESET
  print "\r\n"

install_command = package_manager + " install " + " ".join(to_install)
print "Running the command: " + install_command
user_response = 'Y'
#user_response = raw_input('Is this ok? [Y/n]')
if user_response != 'n':
  install_list = ['sudo', package_manager, 'install', '-y']
  if len(to_install) < 2:
    install_list.append(to_install)
  else:
    install_list.extend(to_install)
  output = subprocess.Popen(install_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  package_manager_response = output.stdout.read()
  package_manager_response_error = output.stderr.read()
  print package_manager_response_error
  print package_manager_response
