
import argparse
from poem import Poem

def main():

    parser = argparse.ArgumentParser(prog='Shalk', description='The best poem generator ever!')
    parser.add_argument('-t', '--type', help='Poem type', choices=['haiku', 'tanka', 'limerick', 'quatrain'], default='haiku') #TODO: add others
    parser.add_argument('-n', '--quantity', help='Quantity of poems generated', default=10)
    parser.add_argument('-s', '--smoothing', help='Smoothing algorithm', choices=['linear', 'backoff'], default='backoff')
    args = parser.parse_args()

    p = Poem(ptype=args.type, smoothing=args.smoothing)

    for x in range(0, args.quantity):
        print '*** HOT NEW POEM COMING RIGHT UP!!! ***'
        text = p.generate()
        if not text:
            print 'Yeah, not this time... Let me try again!'
            print '======================================'
            continue

        print text
        print '======================================'
    print '*** That\'s it, folks!!! ***'

if __name__ == '__main__':
    main()