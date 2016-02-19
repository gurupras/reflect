import os,sys,argparse
import requests

import logging
try:
	from pycommons import generic_logging
	generic_logging.init(level=logging.INFO)
except:
	pass
logger = logging.getLogger(__file__)

def process(server, port):
	# Get the json
	req = requests.get(server + ':' + str(port) + '/reflect')

	import pdb
	pdb.set_trace()
	# TODO: Process it
	pass

def setup_parser():
	parser = argparse.ArgumentParser()

	parser.add_argument('--server', type=str, default='http://twoseven.xyz',
			help='Server to connect to')
	parser.add_argument('--port', type=int, default=31257,
			help='Port to connect to')

	return parser

def main(argv):
	parser = setup_parser()
	args = vars(parser.parse_args(argv[1:]))

	process(**args)

if __name__ == '__main__':
	main(sys.argv)

