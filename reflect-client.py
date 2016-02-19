import os,sys,argparse
import json
import requests
import subprocess

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
				logger.error("Failed to install packages using command: '%s'" % (command))
			else:
				logger.info("Successfully processed packages target '%s'" % (target))
		elif attr['type'] == 'file':
			# Set ID to be target
			attr['id'] = target
			req = requests.get(base_url + '/file', params=attr)
			# The data of this request is the file content itself
			path = os.path.join(outdir, attr['path'])
			path = path.replace('~', os.environ['HOME'])
			try:
				directory = os.path.dirname(path)
				if not os.path.exists(directory):
					os.makedirs(directory)
			except Exception, e:
				logger.warn("Failed to makedirs(): %s" % (e.message))

			try:
				with open(path, 'w') as f:
					f.write(req.text)
				logger.info("Processed target '%s' to file: %s'" % (target, path))
			except Exception, e:
				logger.error("Failed to write file: %s" % (e.message))



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

