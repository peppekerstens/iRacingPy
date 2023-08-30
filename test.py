import argparse, sys

parser=argparse.ArgumentParser()

parser.add_argument("--bar", help="Do the bar option")
parser.add_argument("--foo", help="Foo the program")

args=parser.parse_args()

print(f"Args: {args}\nCommand Line: {sys.argv}\nfoo: {args.foo}")
print(f"Dict format: {vars(args)}")