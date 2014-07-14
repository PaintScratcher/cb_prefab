#!/usr/bin/env python2.7
# -*- mode: Python;-*-

# A tool for automatically generating Couchbase Server vagrant files

# IMPORTS
import argparse
import os
import sys

# FLAGS
parser = argparse.ArgumentParser(description='Automatically generate vagrant configurations')
parser.add_argument("-os", '--os', help='desired operating system', metavar='')
parser.add_argument("-n", "--nodes", help='number of nodes to provision', metavar='')
parser.add_argument("-v", "-version", help='couchbase version', metavar='')
parser.add_argument("-a", "-ask", help='provide cli input for all options', metavar='')

args = parser.parse_args()

# Define Variables and take user input if no flags set

if args.v:
	version = args.v
elif args.a:
	version = str(raw_input('Couchbase version? (x.x.x): '))
else:
	version = '3.0.0'

if args.nodes:
	no_of_nodes = args.nodes
elif args.a:
	no_of_nodes = str(raw_input('Number of nodes?: '))
else:
	no_of_nodes = '1'

if args.os:
	OSname = args.os
elif args.a:
	OSname = str(raw_input('OS? (NameVersion): '))
else:
	OSname = 'Ubuntu14'

if 'ubuntu' in OSname.lower():
	if '10' in OSname:
		OSname = 'Ubuntu10'
	elif '12' in OSname:
		OSname = 'Ubuntu12'
	elif '14' in OSname:
		OSname = 'Ubuntu14'
	else:
		print 'Unrecognised OS'
		sys.exit(0)
elif 'rhel' in OSname.lower() or 'centos' in OSname.lower():
	if '5' in OSname:
		OSname = 'CentOS5'
	elif '6' in OSname:
		OSname = 'CentOS6'
	else:
		print 'Unrecognised OS'
		sys.exit(0)

ip_address_base = "192.168.71.10%d"
box = "puppetlabs/centos-6.5-64-puppet"

#Vagrant File
lines_vagr = ['# Couchbase Server Clustering vagrant file.',
				'# Generated automatically by prefab!\n',
				'Vagrant.configure("2") do |config|\n',
				'	# Server version',
				'	version = "' + version + '"\n',
				'	# Number of nodes to provision',
				'	num_nodes = ' + no_of_nodes + '\n',
				'	# IP Address Base for private network',
				'	ip_addr_base = "' + ip_address_base + '"\n',
				'	# Define Number of RAM for each node',
				'	config.vm.provider :virtualbox do |v|',
				'		v.customize ["modifyvm", :id, "--memory", 1024]',
				'	end\n',
				'	# Provision the server itself with puppet',
				'	config.vm.provision :puppet\n',
				'	config.vm.box = "' + box + '"\n',
				'	# Provision Config for each of the nodes',
				'	1.upto(num_nodes) do |num|',
				'		config.vm.define "node#{num}" do |node|',
				'			node.vm.network :private_network, :ip => ip_addr_base % num',
				'			node.vm.provider "virtualbox" do |v|',
				'				v.name = "Couchbase Server #{version} ' + OSname + ' Node #{num}"',
				'			end',
				'		end',
				'	end\n',
				'end',

				]

# Manifest File
lines_mani = ['# ===',
							'# Install and Run Couchbase Server',
							'# ===\n',
							'$version = "' + version + '"',
							'$stem = "couchbase-server-enterprise_centos6_x86_64_${version}"',
							'$suffix = $operatingsystem ? {',
							'	Ubuntu +> ".deb"',
							'	CentOS => ".rpm"',
							'}',
							'$filename = "$stem$suffix"\n',
							'# Download the Sources',
							'exec { "couchbase-server-source":',
							'  command => "/usr/bin/wget http://packages.northscale.com/latestbuilds/3.0.0/$filename",',
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
							'ource => "/vagrant/$filename",',
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


#Export files
with open('Vagrantfile', 'w') as f:
	f.write('\n'.join(lines_vagr))

filename = "./manifests/default.pp"
dir = os.path.dirname(filename)

try:
	os.stat(dir)
except:
	print "No directory " + dir
	os.mkdir(dir)

with open (filename, 'w') as f:
	f.write('\n'.join(lines_mani))

print "Created a " + no_of_nodes + " node cluster running cb version " + version + " on " + OSname
