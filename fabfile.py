#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from shutil import copytree

from fabric.api import cd, run, local, lcd, put
from fabric.contrib.files import exists

SERVICE_NAME = 'crypto'

BUILD_PATH = 'build'
BUILD_FILENAME = 'build.tar.gz'
BUILD_FOLDERS = ['app', 'requirements', 'etc']

APP_PATH = 'current'
DEPLOY_PATH = 'deploy'
BACKUP_PATH = 'backup'
VENV_PATH = 'venv'
LOG_PATH = 'logs'


def prepare_destination_host():
    """
    Init destination host structure for project

    """
    if not exists(APP_PATH):
        run(f'mkdir -p {APP_PATH}')

    if not exists(VENV_PATH):
        run(f'python3.8 -m venv {VENV_PATH}')
        run(f'{VENV_PATH}/bin/pip install --upgrade pip')

    if not exists(LOG_PATH):
        run(f'mkdir -p {LOG_PATH}')

    if exists(DEPLOY_PATH):
        run(f'rm -rf {DEPLOY_PATH}')


def deployment():
    """
    Deploy app and server configs
    """

    # make local build
    os.mkdir(BUILD_PATH)
    for folder in BUILD_FOLDERS:
        copytree(folder, os.path.join(BUILD_PATH, folder))
    with lcd(BUILD_PATH):
        local(f'tar -czf ../{BUILD_FILENAME} .')

    # load build to host
    run('mkdir -p %s' % DEPLOY_PATH)
    put(BUILD_FILENAME, DEPLOY_PATH)

    with cd(DEPLOY_PATH):
        run(f'tar -xzf {BUILD_FILENAME}')
    run(f'{VENV_PATH}/bin/pip install -r %s' % os.path.join(DEPLOY_PATH, 'requirements', 'common.txt'))

    if exists(BACKUP_PATH):
        run('rm -rf %s' % BACKUP_PATH)
    run('mv %s %s' % (APP_PATH, BACKUP_PATH))
    run('mv %s %s' % (DEPLOY_PATH, APP_PATH))
    run('supervisorctl restart crypto:*')

