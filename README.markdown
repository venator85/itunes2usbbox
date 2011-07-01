itunes2usbbox
=============

A Python script to export iTunes playlists to an external memory to be used in car USB boxes.

* **Author**: Alessio Bianchi
* **System**: Mac OS X
* **Dependencies**: `appscript` (<http://appscript.sourceforge.net/py-appscript/install.html>) or installed via `sudo easy_install appscript`

Usage
-----

    ./itunes2usbbox.py <external_memory_volume> <playlist1> [playlist2] [playlist3]...

Example:

    ./itunes2usbbox.py /Volumes/PENDRIVE Bach Mozart Baroque

This will create the following directories:

* `/Volumes/PENDRIVE/CD01/` containing the tracks in the `Bach` playlist
* `/Volumes/PENDRIVE/CD02/` containing the tracks in the `Mozart` playlist
* `/Volumes/PENDRIVE/CD03/` containing the tracks in the `Baroque` playlist

The filename of each track in these directories is composed by a track number and the track title.

Implementation
--------------

`appscript` is used to interface with iTunes.

For each passed playlist, the script will create a temporary working directory under `/tmp/`. It will extract the audio file paths of each track in the playlist and create symbolic links to them in the working directory. It then uses `rsync` to synchronize the working directory with the corresponding `CDxx` directory in the external memory. Extraneous files in the `CDxx` directory will be deleted.

USB Box compatibility
---------------------

The directory structure created by this script is specifically targeted to [XCarlink](http://www.xcarlink-store.com/) USB boxes. Other devices may or may not work.