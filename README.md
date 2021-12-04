# python-fu
https://bugs.launchpad.net/ubuntu/+source/gimp/+bug/1881684

```
sudo apt install python-cairo python-gobject-2
wget http://mirror.ip-projects.de/ubuntu/pool/universe/p/pygtk/python-gtk2_2.24.0-6_amd64.deb
wget http://ftp.de.debian.org/debian/pool/main/g/gimp/gimp-python_2.10.8-2_amd64.deb
sudo dpkg -i python-gtk2_2.24.0-6_amd64.deb
sudo dpkg -i gimp-python_2.10.8-2_amd64.deb
```

https://sites.google.com/site/non2title/

How to run gmip
```
gimp -id --batch-interpreter python-fu-eval -b "import sys;sys.path=['.']+sys.path;import batch;batch.main()" -b "pdb.gimp_quit(1)"
```

GIMP FONT
https://www.1001fonts.com/qarmic-sans-font.html