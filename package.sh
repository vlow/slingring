#!/bin/bash
VERSION=0.8.2
SOURCEDIR=$(pwd)
TEMPDIR=$(mktemp -d)

# create target layout
BIN_DIR=$TEMPDIR/usr/bin
SLINGRING_DIR=$TEMPDIR/usr/share/slingring
SCHROOT_DIR=$TEMPDIR/etc/schroot

mkdir -p $BIN_DIR
mkdir -p $SLINGRING_DIR
mkdir -p $SCHROOT_DIR
chmod -R 755 $TEMPDIR/usr/
chmod -R 755 $TEMPDIR/etc/

# copy files to target layout
cp -r $SOURCEDIR/slingring-tools $SLINGRING_DIR
cp -r $SOURCEDIR/files/templates $SLINGRING_DIR
cp -r $SOURCEDIR/files/schroot/* $SCHROOT_DIR
cp -r $SOURCEDIR/slingring $BIN_DIR

# build packages
fpm -s dir -t rpm -n slingring -v $VERSION -a noarch -d python3 -d python3-PyYAML -d python3-jinja2 -d ansible -d schroot -d gnupg -d debootstrap -d figlet --after-install create-symlinks.sh --after-remove remove-symlinks.sh -C $TEMPDIR .
fpm -s dir -t pacman -n slingring -v $VERSION -a noarch -d python -d python-yaml -d python-jinja -d ansible -d schroot -d gnupg -d debootstrap -d figlet --after-install create-symlinks.sh --after-remove remove-symlinks.sh -C $TEMPDIR .
fpm -s dir -t deb -n slingring -v $VERSION -a noarch -d python3 -d python3-yaml -d python3-jinja2 -d ansible -d schroot -d gnupg -d debootstrap -d figlet --after-install create-symlinks.sh --after-remove remove-symlinks.sh -C $TEMPDIR .

rm -rf $TEMPDIR
