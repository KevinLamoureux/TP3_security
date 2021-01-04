import argparse
from src.module import generate, send, receive

def arguments_parse():
	# specif arguments
	parser = argparse.ArgumentParser(description="Generate, send and receive message", prog="main")

	parser.add_argument("dir", help="The directory that stores the pads")
	parser.add_argument("f", nargs='?', help="File to read", type=str)
	groupMode = parser.add_mutually_exclusive_group()
	groupMode.add_argument("-g", "--generate", help="Change program mode(Generate)", action="store_true")
	groupMode.add_argument("-s", "--send", help="Change program mode(Send)", action="store_true")
	groupMode.add_argument("-r", "--receive", help="Change program mode(Receive)", action="store_true")

	group = parser.add_mutually_exclusive_group()
	group.add_argument("-f", "--filename", help="Write the text contained in the file", type=str)
	group.add_argument("-t", "--sometext", help="Write the text as argument", type=str)

	args = parser.parse_args()

	if((args.generate or args.receive) and (args.filename is not None or args.sometext is not None)):
		parser.error("--generate or --receive not accept --filename or --sometext argument")
	if(args.receive and args.f is None):
		parser.error("--receive need to fileName")
	print(args)

	if(args.send):
		send(args.dir)
	elif(args.receive):
		receive(args.dir)
	else:
		generate(args.dir)

arguments_parse()