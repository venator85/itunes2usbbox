#!/usr/bin/env python

# author: Alessio Bianchi <venator85 at gmail.com

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import subprocess
import math
from appscript import *

colors = {'none': '\033[0m',
	'black': '\033[0;30m',		'bold_black': '\033[1;30m',
	'red': '\033[0;31m',		'bold_red': '\033[1;31m',
	'green': '\033[0;32m',		'bold_green': '\033[1;32m',
	'yellow': '\033[0;33m',		'bold_yellow': '\033[1;33m',
	'blue': '\033[0;34m',		'bold_blue': '\033[1;34m',
	'magenta': '\033[0;35m',	'bold_magenta': '\033[1;35m',
	'cyan': '\033[0;36m',		'bold_cyan': '\033[1;36m',
	'white': '\033[0;37m',		'bold_white': '\033[1;37m'}

def printmsg(msg):
	print "%s>> %s%s" % (colors['bold_blue'], msg, colors['none'])

def printerr(msg):
	print "%s!! %s%s" % (colors['bold_red'], msg, colors['none'])

def printwarn(msg):
	print "%s!! %s%s" % (colors['bold_yellow'], msg, colors['none'])

# Run a command synchronously, redirecting stdout and stderr to strings
def runcmd(cmd, cwd=None):
	pipe = subprocess.Popen(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	(stdout, stderr) = pipe.communicate()	# wait for process to terminate and return stdout and stderr
	return {'stdout': stdout.strip(), 'stderr': stderr.strip(), 'retcode': pipe.returncode}

# Run a command synchronously, sending stdout and stderr to shell
def runcmd2(cmd, cwd=None):
	pipe = subprocess.Popen(cmd, shell=True, cwd=cwd, stdout=None, stderr=None)
	pipe.communicate()	# wait for process to terminate
	return pipe.returncode

def digits(n):
	if n == 0:
		return 1
	return int(math.floor(math.log10(n)) + 1)

iTunes = app('iTunes')
playlists = iTunes.user_playlists()

def find_playlist(name):
	for pl in playlists:
		if pl.name() == name:
			return pl
	return None

def get_songs(playlist_name):
	pl = find_playlist(playlist_name)
	if pl == None:
		return None
	songs = []
	tracks = pl.file_tracks()
	for tr in tracks:
		path = tr.location().path
		songs.append(path)
	return songs

def create_links(songs):
	dir_r = runcmd("mktemp -d /tmp/itunes2usbbox-XXXX")
	if dir_r['retcode'] != 0:
		printerr("mktemp error: %s" % (dir_r['stderr']))
		return None
	dir = dir_r['stdout']
	
	songs_len = len(songs)
	trackno_len = digits(songs_len)
	for i in range(songs_len):
		s = songs[i]
		tmp = s.split('/')
		trackno = str(i).rjust(trackno_len, '0')
		s_dest = "%s/%s_%s" % (dir, trackno, tmp[-1])
		print s_dest
		os.symlink(s, s_dest)
	
	return dir

def get_external_dirname(n):
	return "CD%s" % (str(n).rjust(2, '0'))

def main(argv):
	memory_dir_base = argv[1]
	playlists = argv[2:]

	cur_playlist = 0
	for pl in playlists:
		printwarn("Processing playlist '%s'" % (pl))
		songs = get_songs(pl)
		if songs == None:
			continue
		local_dir = create_links(songs) + "/"
		if local_dir == None:
			continue
		cur_playlist += 1
		memory_dir = "%s/%s" % (memory_dir_base, get_external_dirname(cur_playlist));
		printmsg("Rsyncing '%s' to '%s'" % (local_dir, memory_dir))
		runcmd2("rsync -LrtcPh --delete '%s' '%s'" % (local_dir, memory_dir))

if __name__ == "__main__":
	if len(sys.argv) >= 3:
		main(sys.argv)
	else:
		printerr("usage: %s <external_memory_volume> <playlist1> [playlist2] [playlist3]..." % (sys.argv[0]))
