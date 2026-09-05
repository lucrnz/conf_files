#!/bin/bash

chmod_test() {
    test $1 $3 && chmod -v $2 $3
}

chmod_test -d 700 ~/.ssh
chmod_test -f 644 ~/.ssh/authorized_keys
chmod_test -f 644 ~/.ssh/known_hosts
chmod_test -f 644 ~/.ssh/config

chmod_test -f 600 ~/.ssh/id_ed25519
chmod_test -f 644 ~/.ssh/id_ed25519.pub

chmod_test -f 600 ~/.ssh/id_rsa
chmod_test -f 644 ~/.ssh/id_rsa.pub
