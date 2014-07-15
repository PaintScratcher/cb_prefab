#!/usr/bin/env python2.7
# -*- mode: Python;-*-

# A tool for automatically generating Couchbase Server vagrant files

# IMPORTS
import argparse
import os
import sys

# Flags for the command line interface
parser = argparse.ArgumentParser(description='Automatically generate vagrant configurations')
parser.add_argument("-os", '--os', help='desired operating system', metavar='')
parser.add_argument("-n", "--nodes", help='number of nodes to provision', metavar='')
parser.add_argument("-v", "-version", help='couchbase version', metavar='')
parser.add_argument("-a", "-ask", help='provide cli input for all options', metavar='')
parser.add_argument("-i", "--ip", help='base ip address for the cluster', metavar='')

args = parser.parse_args()

### DEFINITIONS ###

# Define Variables and take user input if no flags set

if args.v:	# Define Couchbase server version
	version = args.v
elif args.a:
	version = str(raw_input('Couchbase version? (x.x.x): '))
else:
	version = '3.0.0'

if args.nodes: # Define the number of nodes to be provisioned
	no_of_nodes = args.nodes
elif args.a:
	no_of_nodes = str(raw_input('Number of nodes?: '))
else:
	no_of_nodes = '1'

if args.os: # Define the Operating system for the cluster
	OSname = args.os
elif args.a:
	OSname = str(raw_input('OS? (NameVersion): '))
else:
	OSname = 'Ubuntu14'

if args.ip: # Define the base ip address for the cluster
	ip = args.ip
elif args.a:
	ip = str(raw_input('Base IP Address?: '))
else:
	ip = "192.168.68"

# Parse though the given imputs to generate definitions

if '3.' in version: # Change the download location for 3 beta builds
	command = 'http://packages.northscale.com/latestbuilds/3.0.0/$filename'
	stem = "couchbase-server-enterprise_centos6_x86_64_${version}"
else:
	command = 'http://packages.couchbase.com/releases/${version}/${filename}'
	stem = "couchbase-server-enterprise_${version}_x86_64."


node_config = '			# box pre-configured'
if 'ubuntu' in OSname.lower(): # Change the vagrant base box for each OS
	#if '10' in OSname: REMOVING UBUNTU10 FOR THE MOMENT
	#	OSname = 'Ubuntu10'
	if '12' in OSname:
		OSname = 'Ubuntu12'
		box = 'config.vm.box_url = "http://files.vagrantup.com/precise64.box"'
		node_config = '			node.vm.box = "precise64"'
	elif '14' in OSname:
		OSname = 'Ubuntu14'
		box = 'config.vm.box = "ubuntu/trusty64"'
	else:
		print 'Unrecognised OS'
		sys.exit(0)
elif 'rhel' in OSname.lower() or 'centos' in OSname.lower():
	if '5' in OSname:
		OSname = 'CentOS5'
		box = 'config.vm.box_url = "https://dl.dropbox.com/u/17738575/CentOS-5.8-x86_64.box"'
		node_config = '			node.vm.box = "centos5u8_x64"'
	elif '6' in OSname:
		OSname = 'CentOS6'
		box = 'config.vm.box = "puppetlabs/centos-6.5-64-puppet"'
	else:
		print 'Unrecognised OS'
		sys.exit(0)

### EXPORT ###

#Vagrant File Setup
lines_vagr = ['# Couchbase Server Clustering vagrant file.',
				'# Generated automatically by prefab!\n',
				'Vagrant.configure("2") do |config|\n',
				'	# Server version',
				'	version = "' + version + '"\n',
				'	# Number of nodes to provision',
				'	num_nodes = ' + no_of_nodes + '\n',
				'	# IP Address Base for private network',
				'	ip_addr_base = "' + ip + '"\n',
				'	# Define Number of RAM for each node',
				'	config.vm.provider :virtualbox do |v|',
				'		v.customize ["modifyvm", :id, "--memory", 1024]',
				'	end\n',
				'	# Provision the server itself with puppet',
				'	config.vm.provision :puppet\n',
				'	'+ box + '\n',
				'	# Provision Config for each of the nodes',
				'	1.upto(num_nodes) do |num|',
				'		config.vm.define "node#{num}" do |node|',
						node_config,
				'			node.vm.network :private_network, :ip => ip_addr_base % num',
				'			node.vm.provider "virtualbox" do |v|',
				'				v.name = "Couchbase Server #{version} ' + OSname + ' Node #{num}"',
				'			end',
				'		end',
				'	end\n',
				'end',

				]

# Manifest File Setup
lines_mani = ['# ===',
							'# Install and Run Couchbase Server',
							'# ===\n',
							'$version = "' + version + '"',
							'$stem = "' + stem + '"',
							'$suffix = $operatingsystem ? {',
							'	Ubuntu => ".deb"',
							'	CentOS => ".rpm"',
							'}',
							'$filename = "$stem$suffix"\n',
							'# Download the Sources',
							'exec { "couchbase-server-source":',
							'  command =>  "/usr/bin/wget '+ command + '",',
							'	cwd => "/vagrant/",',
							'	creates => "/vagrant/$filename",',
							'	before => Package[\'couchbase-server\']',
							'}\n',
							'# Install Coucbase Server',
							'package { "couchbase-server":',
							'	provider => $operatingsystem ? {',
							'		Ubuntu => dkpg,',
							'		CentOS => rpm,',
							'	},',
							'ensure => installed,',
							'source => "/vagrant/$filename",',
							'}\n',
							'# Ensure firewall is off (some CentOS images have firewall on by default).',
							'service { "iptables":',
							'	ensure => "stopped",',
							'	enable => false,',
							'}\n',
							'# Ensure the service is running',
							'	service { "couchbase-server":',
							'	ensure => "running",',
							'	require => Package["couchbase-server"]',
							'}\n'
				]


# Export files
with open('Vagrantfile', 'w') as f:
	f.write('\n'.join(lines_vagr))

filename = "./manifests/default.pp"
dir = os.path.dirname(filename)

try:  # Check to see if the manifest directory / file has been created (and create it)
	os.stat(dir)
except:
	print "No directory " + dir
	os.mkdir(dir)

with open (filename, 'w') as f:
	f.write('\n'.join(lines_mani))

print "Created a " + no_of_nodes + " node cluster running cb version " + version + " on " + OSname
