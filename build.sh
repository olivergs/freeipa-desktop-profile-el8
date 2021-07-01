#!/bin/bash

VERSION="0.0.8"

if [[ ! -f freeipa-desktop-profile-$VERSION.tar.gz ]]; then
    wget https://github.com/abbra/freeipa-desktop-profile/archive/refs/tags/$VERSION.tar.gz -O freeipa-desktop-profile-$VERSION.tar.gz
fi

cp freeipa-desktop-profile-$VERSION.tar.gz ~/rpmbuild/SOURCES/

rpmbuild -ba freeipa-desktop-profile.spec

cp ~/rpmbuild/RPMS/freeipa-desktop-profile*.rpm .

