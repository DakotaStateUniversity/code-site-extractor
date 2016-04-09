from icse import extractor
import time
import argparse
import os.path
import sys

#'buffer_read', 'division_by_zero', 'variable_access', 'null_ptr', 'int_overflow', 'int_underflow', 'write_what_where', 'return'
types = ['all', 'buffer_write']

parser = argparse.ArgumentParser(description='Extract sites from file(s) and output them to file.')

parser.add_argument('source', help='source file or directory name', 
          metavar='srcfile')
parser.add_argument('-o', '--output-file', help='site output file name', 
          metavar='outfile')
parser.add_argument('-s', '--sites', default='all', metavar='type',
          choices=types,
          help='which type of site to search for ' + str(types))
#NOT IMPLEMENTED
#parser.add_argument('--threads', default=2,
#          help='NOT IMPLEMENTED how many threads to run', type=int)


args = parser.parse_args()

if not os.path.exists(args.source):
  print("File or directory '%s' does not exist!" % args.source)
  sys.exit(1)

if args.output_file:
  print("output-file: '%s'" % args.output_file)
else:
  print("no output-file specified, using sites_list.csv")
  args.output_file = 'sites_list.csv'

print("sites: '%s'" % args.sites)


print("Parsing files and Building AST trees, this may take a while...")
sites_extractor = extractor.Extractor(args.source, args.sites)
#sites_extractor = extractor.Extractor("selected_Juliet_tests/", 'buffer_write')

print("Extracting buffer write sites...")
sites = sites_extractor.buffer_write_sites()

#csv_start = time.clock()

print("generating csv file")
extractor.Extractor.to_csv(sites, args.output_file)

#csv_end = time.clock()
#print("csv time: {0}".format(csv_end - csv_start))


#if __name__ == '__main__':
