import os,sys,argparse
import json
import requests
import subprocess
import hashlib

import logging
try:
	from pycommons import generic_logging
	generic_logging.init(level=logging.INFO)
except:
	logging.basicconfig(level=logging.DEBUG)
logger = logging.getLogger(__file__)

def process(server, port, outdir=''):
	# Get the json
	base_url = server + ':' + str(port)
	logger.debug("Requesting server for reflection")
	req = requests.get(base_url + '/reflect')
	logger.debug("Server responds with status code: %d" % (req.status_code))

	# Process it
	reflection = req.json()

	for target, attr in reflection.iteritems():
		logger.debug("Processing target: " + target)
		if attr['type'] == 'packages':
			command = attr['command'] + ' ' + attr['packages']
			p = subprocess.Popen(command, shell=True)
			p.wait()
			if p.returncode != 0:
				logger.error("\tFailed to install packages using command: '%s'" % (command))
			else:
				logger.info("\tSuccessfully processed packages target '%s'" % (target))
		elif attr['type'] == 'file':
			attr = dict(attr)
			path = os.path.join(outdir, attr['path'])
			path = path.replace('~', os.environ['HOME'])
			# Check if we have a version of this file
			if os.path.exists(path):
				attr['hash'] = hashlib.sha256(open(path, 'r').read()).hexdigest()
			# Set ID to be target
			attr['id'] = target
			req = requests.get(base_url + '/file', params=attr)
			# Check response
			response = req.json()
			if response['match'] is True:
				# We have nothing to do
				logger.debug("\tHashes match!")
				logger.info("\tSuccessfully processed target '%s'" % (target))
				continue
			try:
				directory = os.path.dirname(path)
				if not os.path.exists(directory):
					os.makedirs(directory)
			except Exception, e:
				logger.warn("\tFailed to makedirs(): %s" % (e.message))

			try:
				with open(path, 'w') as f:
					f.write(req.text)
				logger.info("\tSuccessfully processed target '%s' to file: %s'" % (target, path))
			except Exception, e:
				logger.error("\tFailed to write file: %s" % (e.message))



def setup_parser():
	parser = argparse.ArgumentParser()

	parser.add_argument('--server', type=str, default='http://twoseven.xyz',
			help='Server to connect to')
	parser.add_argument('--port', type=int, default=31257,
			help='Port to connect to')
	parser.add_argument('--outdir', type=str, default='',
			help='Redirect all file output to this base path')
	return parser

def main(argv):
	parser = setup_parser()
	args = vars(parser.parse_args(argv[1:]))

	process(**args)

if __name__ == '__main__':
	main(sys.argv)

