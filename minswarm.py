#!/usr/bin/env python
'''
Salt Minion Swarm
'''

import optparse
import os
import random
import string
import sys
import subprocess
import time
import yaml
import salt.config
import salt.loader

TYP = [
    'bld',
    'dev',
    'eng',
    'fin',
    'hr',
    'mgnt',
    'mrktg',
    'mnfg',
    'pm',
    'qa',
    'rel',
    'rnd',
    'sales',
    'sup',
    ]

## -------------------------------------
def prgopts():
    '''
    Parse program options
    '''

    parser = optparse.OptionParser()
    parser.add_option(
        '-n',
        dest='num',
        default=5,
        type='int',
        help='The number of minions to start. (Default: %default)')
    parser.add_option(
        '-m',
        dest='master',
        default='127.0.0.1',
        help='The location of the salt master to connect to. (Default: %default)')
    parser.add_option(
        '-i',
        dest='id',
        default=1,
        type='int',
        help='ID for the minions on this box (1-99). Used when minions from '
             'many systems and masters are tested together. (Default: %default)')
    parser.add_option(
        '-c',
        dest='cf',
        default='/etc/salt/minion',
        help='Alternate minion configuration file. (Default: %default)')


    options, args = parser.parse_args()
    if not options.master:
        parser.print_help()
        sys.exit(1)
    return options.__dict__


## -------------------------------------
def idgen( size=4, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size) )


## -------------------------------------
def ipgen( part1 = "1", part2 = 1 ):
    ip = "10." + str(part1) + "." + str(part2) + "."
    return ( ip + str(random.randint(1, 254)) )


## -------------------------------------
def mkConfigDir( __grains__, m_id, m_master, num, s_vers ):
    '''
    Create config dir with empty cache and pki dirs
    '''
    os_str = str(__grains__['os']).replace(' ', '_' )
    minion_str = "%s-%s-%s-%s" %( os_str, '{:02d}'.format( m_id ), random.choice(TYP), idgen() )
    baseDir = os.path.join( "/tmp/minswarm", minion_str )
    cacheDir = os.path.join( baseDir, "cache" )
    pkiDir = os.path.join( baseDir, "pki" )
    pidFile = os.path.join( baseDir, "pid" )
    minionConf = os.path.join( baseDir, "minion" )
    minionLog = os.path.join( baseDir, "minion.log" )

    ver = random.choice(saltvers)
    minion_ip = ipgen( part1=m_id, part2=num )

    os.makedirs( cacheDir )
    os.makedirs( pkiDir )

    fh = open( minionConf, "w" )
    fh.write( "cachedir: %s\n" % cacheDir )
    fh.write( "grains:\n" )
    fh.write( "  cpuarch:\n" )
    fh.write( "    %s\n" % __grains__['cpuarch'] )
    fh.write( "  host:\n" )
    fh.write( "    %s\n" % minion_str )
    fh.write( "  id:\n" )
    fh.write( "    %s\n" % minion_str )
    fh.write( "  ipv4:\n" )
#    fh.write( "    - 127.0.0.1\n" )
    fh.write( "    - %s\n" % minion_ip )
    fh.write( "  master:\n" )
    fh.write( "    %s\n" % m_master )
    fh.write( "  mem_total:\n" )
    fh.write( "    %s\n" % __grains__['mem_total'] )
    fh.write( "  nodename:\n" )
    fh.write( "    %s\n" % minion_str )
    fh.write( "  num_cpus:\n" )
    fh.write( "    %s\n" % __grains__['num_cpus'] )
    fh.write( "  num_gpus:\n" )
    fh.write( "    %s\n" % __grains__['num_gpus'] )
    fh.write( "  os:\n" )
    fh.write( "    %s\n" % __grains__['os'] )
    fh.write( "  os_family:\n" )
    fh.write( "    %s\n" % __grains__['os_family'] )
    # osfullname is not a grain found in all the OS's I've tested with
    if 'osfullname' in __grains__:
        fh.write( "  osfullname:\n" )
        fh.write( "    %s\n" % __grains__['osfullname'] )
    fh.write( "  osrelease:\n" )
    fh.write( "    %s\n" % __grains__['osrelease'] )
    with open('saltver.yaml') as f:
        rec = yaml.load(f)
        if ver in rec:
            fh.write( "  saltversion:\n" )
            fh.write( "    %s\n" % ver )
            fh.write( "  saltversioninfo:\n" )
            for idx in rec[ver]:
                fh.write( "    - %s\n" % str(idx) )

    fh.write( "  virtual:\n" )
    fh.write( "    physical\n" )
    fh.write( "id: %s\n" % minion_str )
    fh.write( "log_file: %s\n" % minionLog )
    fh.write( "master: %s\n" % m_master )
    fh.write( "multiprocessing: False\n" )
    fh.write( "pki_dir: %s\n" % pkiDir )
    fh.write( "user: root\n" )
    fh.close()

    cmd = 'salt-minion --config-dir=%s --pid-file=%s --daemon' % (baseDir, pidFile)
    print( minion_str )
    subprocess.call( cmd, shell=True )

## =========================================================
if __name__ == '__main__':
    opts = prgopts()

    __opts__ = salt.config.minion_config( opts['cf'] )
    __grains__ = salt.loader.grains(__opts__)

    count = opts['num']
    minion_id = opts['id']
    minion_master = opts['master']
    network_num = 1

    saltvers = []
    with open('saltver.yaml') as f:
        rec = yaml.load(f)
        for e in rec:
            saltvers.append( e )

    print( "Starting minions. . ." )


    for n in range(1, count+1):
        if n%20 == 0:
            network_num += 1
        mkConfigDir( __grains__, minion_id, minion_master, network_num, saltvers )

