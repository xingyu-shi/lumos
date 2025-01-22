from lumos.build import build_rag
import argparse

parser = argparse.ArgumentParser(description='lumos', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--source', '-s', help='rag source')
parser.add_argument('--include_exts', help='include file exts', default=['.txt', '.md'], nargs='+')
args = parser.parse_args()

if __name__=='__main__':
    # build_rag.sh('/Users/xingyushi/.notable')
    build_rag('/Users/xingyushi/code/personal/lumos/Crawler/workspace')
    # build_rag(args.source, args.include_exts)
