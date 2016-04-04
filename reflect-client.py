import os,sys,argparse
import json
import subprocess
import hashlib
import urllib, urllib2
import logging
try:
	from pycommons import generic_logging
	generic_logging.init(level=logging.INFO)
except:
	logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__file__)

def process(server, port, outdir=''):
	# Get the json
	base_url = server + ':' + str(port)
	logger.debug("Requesting server for reflection")
	url = base_url + '/reflect'
	req = urllib2.urlopen(url)
	#logger.debug("Server responds with status code: %d" % (req.status_code))

	# Process it
	reflection = json.loads(req.read())

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
			func = globals()[attr['method']]
			func(base_url, target, attr, outdir)

def download(base_url, target, attr, outdir):
		attr = dict(attr)
		path = os.path.join(outdir, attr['path'])
		path = path.replace('~', os.environ['HOME'])
		# Check if we have a version of this file
		if os.path.exists(path):
			attr['hash'] = hashlib.sha256(open(path, 'r').read()).hexdigest()
		# Set ID to be target
		attr['id'] = target
		url_qs = urllib.urlencode(attr)
		url = base_url + '/file' + '?' + url_qs
		logger.info('GET ' + url)
		req = urllib2.urlopen(url)
		# Check response
		response = json.loads(req.read())
		if response['match'] is True:
			# We have nothing to do
			logger.debug("\tHashes match!")
			logger.info("\tSuccessfully processed target '%s'" % (target))
			return
		try:
			directory = os.path.dirname(path)
			if not os.path.exists(directory):
				os.makedirs(directory)
		except Exception, e:
			logger.warn("\tFailed to makedirs(): %s" % (e.message))

		try:
			with open(path, 'w') as f:
				f.write(response['data'])
			logger.info("\tSuccessfully processed target '%s' to file: %s'" % (target, path))
		except Exception, e:
			logger.error("\tFailed to write file: %s" % (e.message))
			import pdb
			pdb.set_trace()
			print ''




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

