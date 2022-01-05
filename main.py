import argparse
from parse_actros_info import main

parser = argparse.ArgumentParser()
parser.add_argument(
    "--count", choices=[1, 2, 3, 4, 5], type=int, default=5,
    help="select pages count to parse", required=True)
args = parser.parse_args()

if args.count:
    main(args.count)
    print("We have parsed actors info from site <www.kino-teatr.ru/kino/acter/w/ros/s/a1>")
