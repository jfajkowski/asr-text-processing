#!/usr/bin/env bash

for file in $@; do
    if [ ! -f $file ]; then
        log -ent "File $file is required!"
        exit 1
    fi
done