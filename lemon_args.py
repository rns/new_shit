import argparse

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--eightbit', action='store_true',
				   help='try to be compatible with 8 bit color mode.')
	parser.add_argument('--dontblink', action='store_true',
				   help='dont blink the cursor.')
	parser.add_argument('--log-events', action='store_true',
				   help='what it says.')
	parser.add_argument('--noalpha', action='store_true',
				   help='avoid alpha blending')
	parser.add_argument('--mono', action='store_true',
				   help='no colors, just black and white')
	parser.add_argument('--webos', action='store_true',
				   help='webos keys hack')
	parser.add_argument('--invert', action='store_true',
				   help='invert colors')
	parser.add_argument('--replay', action='store_true',
				   default=False)
	parser.add_argument('--font_size', action='store_true',
				   default=22)
	parser.add_argument('--log_height', default=4, type=int)
	return parser.parse_args()
#args = parse_args()