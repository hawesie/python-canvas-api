__author__ = 'nah'

from marking import mongodb_store
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Store Canvas API token in database')
    parser.add_argument('key', metavar='K', type=str, nargs=1,
                   help='Your Canvas API access key.')

    args = parser.parse_args()

    store = mongodb_store.SubmissionStore()
    store.store_key(args.key)
 