"""Extractor class file."""

import re
import os
import time
import threading
import queue
import fnmatch
from pycparser import parse_file, c_ast, c_generator
from icse import site
#from ocse.node_visitor import *
from icse import buffer_write

#Path to the c preprocessor
CPPPATH = 'cpp'

class Extractor:
  """Class to extract sites from Juliet 1.2 and check if these sites are buggy
  or not.
  """

  def __init__(self,
      root_path,
      parse_single_cwe=None):
    """root_path is the path where the juliet files to be analyzed are.
    This constructor method prepares all the data structures to receive
    the Synthetic Trees informations from pycparser.
    parse_single_cwe makes ocse run faster by getting results for a
    single cwe. current supported options are:
    'division_by_zero'
    'variable_access'
    'null_ptr'
    'int_of'
    'int_uf'
    'buffer_write'
    'buffer_read'
    'write_what_where'
    'return'
    """
    self.root_path = root_path
    self.parse_single_cwe = parse_single_cwe
    self.files = []
    self.set_files_list()
    self.ast_queue = queue.Queue()
    self.ast_queue_done = False
    self.ast_buffer_writes = queue.Queue()
    self.ast_buffer_reads = queue.Queue()
    self.extract()

  def extract(self):
    """Trigger the threads to generate the ATSs and navigate through them."""
    extract_th = threading.Thread(None, target=self.extract_ast)
    populate_th = threading.Thread(None, target=self.populate_ast_attributes)


    populate_th.start()
    #populate_start = time.clock()
    extract_th.start()
    #extract_start = time.clock()
    
    extract_th.join()
    #extract_end = time.clock()
    populate_th.join()
    #populate_end = time.clock()

    #print("populate time: {0}".format(populate_end - populate_start))
    #print("extract time: {0}".format(extract_end - extract_start))

  def set_files_list(self):
    """Navigates through the filepath tree and appends all C files in the files
    list.
    """
    if os.path.isfile( self.root_path ):
      self.files.append( self.root_path )
    else:
      for root, dirnames, filenames in os.walk(self.root_path):
        for filename in filenames:
          if '.c' in filename[-2:]:
            self.files.append(os.path.join(root, filename))

  def buffer_write_sites(self):
    """Returns list of buffer write sites.
    Buffer write sites are stack and heap based buffer overflows and buffer underwrites.
    """
    sites = []
    while(not self.ast_buffer_writes.empty()):
      buffer_write = self.ast_buffer_writes.get()
      #TODO add line from file as well as generated line to site
      #site_line = self.lines_map["{0}:{1}".format(buffer_write.coord.file, buffer_write.coord.line)]
      codes = (c_generator.CGenerator()).visit(buffer_write)

      if(isinstance(buffer_write.lvalue, c_ast.ArrayRef)):
        if(isinstance(buffer_write.lvalue.name, c_ast.ID)):
          sites.append(site.Site(buffer_write.lvalue.coord.file, "buffer_write", buffer_write.lvalue.coord.line, codes, buffer_write.lvalue.name.name))
        elif(isinstance(buffer_write.lvalue.name, c_ast.StructRef)):
          sites.append(site.Site(buffer_write.lvalue.coord.file, "buffer_write", buffer_write.lvalue.coord.line, codes, str(buffer_write.lvalue.name.name.name) + '.' + str(buffer_write.lvalue.name.field.name)))
      elif(isinstance(buffer_write.lvalue, c_ast.UnaryOp)):
        sites.append(site.Site(buffer_write.lvalue.coord.file, "buffer_write", buffer_write.lvalue.coord.line, codes, buffer_write.lvalue.expr.name))
      else: 
        #PROBABLY DOESN'T NEED TO BE HERE
        sites.append(site.Site(buffer_write.lvalue.coord.file, "buffer_write", buffer_write.lvalue.coord.line, codes, buffer_write.lvalue.name))

    return sites

  @staticmethod
  def to_csv(sites, csv_output_path = r'sites_list.csv'):
    """Prints a list of sites to an csv file."""
    files = set([])
    for site in sites:
      files = files.union(set([site.filename]))

    f = open(csv_output_path, 'w')
    f.write(str('filename' + '\n'))
    f.write(str('type, line, val, code' + '\n\n'))

    for filename in files:
      f.write(str(os.path.basename(filename) + '\n'))
      
      for site in sites:
        if(site.filename == filename):
          f.write(str(site.site_type) + ',' + str(site.line) + ',' + str(site.info) + ',' + str(site.code) + '\n')

      f.write('\n')

    f.close()

  def extract_ast(self):
    """Fills ast_queue with one AST for each file in the filepath."""
    print("STARTED extract_ast thread")
    for file_path in self.files:
      #print("extract_ast: '%s'" % file_path)
      ast = parse_file(file_path, use_cpp=True,
              cpp_path=CPPPATH,
              # removed cpp_arg r'-D_WIN32' 
              # r'-rquoteutils/testcasesupport' needed for #include "std_testcase.h"
              #     may fix by moving location of std_testcase.h
              cpp_args=[r'-Iutils/fake_libc_include', r'-iquoteutils/testcasesupport'],
              #cpp_args=[r'-Iutils/fake_libc_include', r'-iquoteutils/testcasesupport', r'-D_WIN32'],

              )
      self.ast_queue.put(ast)
    self.ast_queue_done = True

  def populate_ast_attributes(self):
    """Calls all the methods to populate each AST list for each site type."""
    print("STARTED populate_ast_attributes thread")
    while(not (self.ast_queue.empty() and self.ast_queue_done)):
      ast = self.ast_queue.get()
      self.ast_queue.task_done()
      #print("populate_ast_attributes")
      buffer_write_th = threading.Thread(None, target=self.populate_ast_buffer_writes, args=(ast,))
      threads = []

      if(self.parse_single_cwe == 'buffer_write' 
        or self.parse_single_cwe == 'all'):
        threads.append(buffer_write_th)

      for thread in threads:
        thread.start()

      for thread in threads:
        thread.join()

  def populate_ast_buffer_writes(self, ast):
    """Calls pycparser node visitor in the ast. puts the buffer write
    nodes in the ast_buffer_writes queue.
    """
    buffer_write_visitor = buffer_write.BufferWriteVisitor()
    buffer_write_visitor.visit(ast)
    for node in buffer_write_visitor.nodes:
      self.ast_buffer_writes.put(node)
