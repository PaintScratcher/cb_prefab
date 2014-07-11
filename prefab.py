#!/usr/bin/env python2.7
# -*- mode: Python;-*-

# READMEEE

import argparse

parser = argparse.ArgumentParser(description='Automatically generate vagrant configurations')
parser.add_argument("-os", '--os', help='desired operating system', metavar='')
parser.add_argument("-n", "--nodes", help='number of nodes to provision', metavar='')
parser.add_argument("-v", "-version", help='couchbase version', metavar='')
parser.add_argument("-a", "-ask", help='provide cli input for all options', metavar='')

args = parser.parse_args()

#Define Variables and take user input if no flags set

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

ip_address_base = "192.168.71.10%d"
box = "puppetlabs/centos-6.5-64-puppet"

print "Created a " + no_of_nodes + " node cluster running cb version " + version + " on " + OSname
#Export files

#Vagrant File
lines = ['# Couchbase Server Clustering vagrant file.',
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

with open('Vagrantfile', 'w') as f:
	f.write('\n'.join(lines))
