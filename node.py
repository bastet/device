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
  if manifest['
