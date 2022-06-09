import argparse


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def coords(s):
    try:
        lista = []
        for y in s.split(';'):
            m = y.split(',')
            lista.append((int(m[0][1:]), int(m[1][:-1])))
        return lista
    except:
        raise argparse.ArgumentTypeError("Coordinates must be (x,y) or (x,y);(x,y)")


def link(s):
    if s == "0":
        return 0
    else:
        return s


def get_args():
    arg_parser = argparse.ArgumentParser(description='''Motion detection''', )

    arg_parser.add_argument(
        '-l', '--link', type=link, default='https://imageserver.webcamera.pl/rec/zakopane/latest.mp4',
        help='Link to camera')
    arg_parser.add_argument(
        '-d', '--debug', type=str2bool, default=False, help='If running a debug mode')
    arg_parser.add_argument(
        '-mul', '--mask-upper-left', type=coords, default=None, help='Upper-left point of rectangle to mask in %')
    arg_parser.add_argument(
        '-mlr', '--mask-lower-right', type=coords, default=None, help='Lower-right point of rectangle to mask in %')
    arg_parser.add_argument(
        '-s', '--smallest_area', type=int, default=1, help='The smallest area to be considered as motion per mille')

    args = arg_parser.parse_args()
    return args


if __name__ == '__main__':
    print(get_args())
