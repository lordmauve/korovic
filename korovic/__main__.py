from .game import Game
from optparse import OptionParser

def main():
    p = OptionParser()
    p.add_option('-l', '--level', type='int', help='Initial level', default=1)
    options, args = p.parse_args()
    g = Game()
    g.start(level=options.level)


if __name__ == '__main__':
    main()
