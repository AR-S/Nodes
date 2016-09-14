#!/bin/env python

# To run: fab deploy
import os
from fabric.api import cd, env, run, put, get
from fabric.contrib.files import exists
from fabric.operations import sudo
from fabric.colors import *

# @note: rest of settings in your ~/.fabricrc file
env.hosts = ['pi@ars-nodes.duckdns.org:2222']

env.app_name = 'massage'

def host_type():
    run('uname -s')

def upload():
    upload = put("website.zip", "website.zip")
    if not upload.succeeded:
        print(red("something went wrong with the upload"))
    else:
        run('unzip -o website.zip')
        sudo('cp -R website/ /var/www')
        sudo("chown -R www-data:www-data /var/www" )

def deploy():
    host_type()
    upload()
