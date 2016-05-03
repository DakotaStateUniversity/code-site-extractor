"""Extractor class file."""

import re
import os
import time
import threading
import queue
import fnmatch
from pycparser import c_ast, c_generator
from icse import site
#from ocse.node_visitor import *
from icse import buffer_write
from icse import buffer_read

from subprocess import Popen, PIPE
from pycparser import CParser

#Path to the c preprocessor
CPPPATH = 'cpp'

def parse_file(filename, use_cpp=False, cpp_path='cpp', cpp_args='',
               parser=None):
  '''Modified version of pycparser's parse_file.

  Args:
    filename (string): Name of file to be parsed
    use_cpp (optional[bool]): True if cpp will be used
    cpp_path (optional[string]): Path to cpp
    cpp_args (optional[string]): Arguments for cpp
    parser (optional[CParser]): Parser to be used

  Returns:
    tuple: (filename, source, AST)

  '''

  with open(filename, 'rU') as f:
    text = f.read()

  if use_cpp:
    processedText = preprocess_file(filename, cpp_path, cpp_args)
  else:
    processedText = text

  if parser is None:
    parser = CParser()
  return (filename, text, parser.parse(processedText, filename))

def preprocess_file(filename, cpp_path='cpp', cpp_args=''):
  '''Preprocesses the file, removes comments, expands macros, handles
  includes.

  Args:
    filename (string): Name of source file to be processed
    cpp_path (optional[string]): Path to cpp
    cpp_args (optional[string]): Arguments for cpp

  Returns:
    Returns preprocessed source code
  '''
  path_list = [cpp_path]
  if isinstance(cpp_args, list):
    path_list += cpp_args
  elif cpp_args != '':
    path_list += [cpp_args]
  path_list += [filename]

  try:
    pipe = Popen(path_list, stdout=PIPE, universal_newlines=True)
    text = pipe.communicate()[0]
  except OSError as e:
    raise RuntimeError("Unable to invoke 'cpp'.  " +
      'Make sure its path was passed correctly\n' +
      ('Original error: %s' % e))

  return text

class Extractor:
  """Class to extract sites from C source code 

  Attributes:
    root_path (string): Path to file or directory with C source files
    parse_single_cwe (string): Type of site(s) to extract
    files (list): All files in root_path
    ast_queue (Queue): Holds tuples (filename, source_code, AST) of each file
      in root_path
    ast_queue_done (bool): True when ast_queue is filled with all ASTs from 
      files in root_path
    ast_buffer_writes (Queue): Holds tuples (node, source_line) for buffer_writes
    ast_buffer_reads (Queue): Holds tuples (node, source_line) for buffer_reads
    parser (CParser): CParser for parsing files and generating AST
  """

  def __init__(self, root_path, parse_single_cwe=None):
    """This constructor method prepares all the data structures to receive
      the Synthetic Trees informations from pycparser.

      Args:
        root_path (string): File or directory with C source code
        parse_single_cwe (optional[string]): Types of sites to extract

      Returns:
        None
    """
    self.root_path = root_path
    self.parse_single_cwe = parse_single_cwe
    self.files = []
    self.set_files_list()
    self.ast_queue = queue.Queue()
    self.ast_queue_done = False
    self.ast_buffer_writes = queue.Queue()
    self.ast_buffer_reads = queue.Queue()
    self.parser = CParser()
    self.generator = c_generator.CGenerator()
    self.extract()

  def extract(self):
    """Trigger the threads to generate the ATSs and navigate through them.
    
    Args:
      None
      
    Returns:
      None
    """
    extract_th = threading.Thread(None, target=self.extract_ast)
    populate_th = threading.Thread(None, target=self.populate_ast_attributes)

    extract_th.start()
    populate_th.start()
    
    extract_th.join()
    populate_th.join()

  def set_files_list(self):
    """Navigates through the filepath tree and appends all C files in the files
    list.

    Args:
      None

    Returns:
      None
    """
    if os.path.isfile( self.root_path ):
      self.files.append( self.root_path )
    else:
      for root, dirnames, filenames in os.walk(self.root_path):
        for filename in filenames:
          if '.c' in filename[-2:]:
            self.files.append( os.path.join( root, filename)  )

  def buffer_write_sites(self):
    """Returns list of buffer write sites.
    Buffer write sites are stack and heap based buffer overflows and buffer underwrites.
    This method goes through each node that was selected by populate_ast_buffer_writes
    method. It grabs the proper information and creates a site that is added
    to a list.

    Args:
      None

    Returns:
      sites (list): Contains list of buffer write sites
    """
    sites = []
    while(not self.ast_buffer_writes.empty()):
      buffer_write = self.ast_buffer_writes.get()
      node = buffer_write[0]
      line = buffer_write[1]

      gen_line = (self.generator).visit(node)

      if(isinstance(node.lvalue, c_ast.ArrayRef)):
        if(isinstance(node.lvalue.name, c_ast.ID)):
          sites.append(site.Site(node.lvalue.coord.file, "buffer_write", node.lvalue.coord.line, line, self.generator.visit(node.lvalue.name)))
        elif(isinstance(node.lvalue.name, c_ast.StructRef)):
          sites.append(site.Site(node.lvalue.coord.file, "buffer_write", node.lvalue.coord.line, line, self.generator.visit(node.lvalue.name)))
      elif(isinstance(node.lvalue, c_ast.UnaryOp)):
        sites.append(site.Site(node.lvalue.coord.file, "buffer_write", node.lvalue.coord.line, line, self.generator.visit(node.lvalue.expr)))
      else: 
        sites.append(site.Site(node.lvalue.coord.file, "buffer_write", node.lvalue.coord.line, line, self.generator.visit(node.lvalue)))

    return sites

  def buffer_read_sites(self):
    """Returns list of buffer read sites.
    Buffer read sites are stack and heap based buffer overflows and buffer underreads.
    This method goes through each node that was selected by populate_ast_buffer_reads
    method. It grabs the proper information and creates a site that is added
    to a list.

    Args:
      None

    Returns:
      sites (list): Contains list of buffer read sites
    """
    sites = []
    while(not self.ast_buffer_reads.empty()):
      buffer_read = self.ast_buffer_reads.get()

      node = buffer_read[0]
      line = buffer_read[1]

      gen_line = (self.generator).visit(node)

      sites.append(site.Site(node.coord.file, "buffer_read", node.coord.line, line, node.name))

    return sites

  @staticmethod
  def to_csv(sites, csv_output_path = r'sites_list.csv'):
    """Prints a list of sites to an csv file.
    
    Args:
      sites (list): Contains Sites that will be written to file
      csv_output_path (optional[string]): Output filename

    Returns:
      None
    """
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
    """Fills ast_queue with one AST for each file in the filepath. Calls
    parse_file method.
    
    Notes: Changes self.ast_queue_done to True when it has finished parsing
      all files.

    Args:
      None
      
    Returns:
      None
    """
    print("STARTED extract_ast thread")
    for file_path in self.files:
      ast = parse_file(file_path, use_cpp=True,
        cpp_path=CPPPATH,
        # removed cpp_arg r'-D_WIN32' 
        # r'-rquoteutils/testcasesupport' needed for #include "std_testcase.h"
        #     may fix by moving location of std_testcase.h
        cpp_args=[r'-Iutils/fake_libc_include', r'-iquoteutils/testcasesupport'],
        #cpp_args=[r'-Iutils/fake_libc_include', r'-iquoteutils/testcasesupport', r'-D_WIN32'],
        parser=self.parser
        )
      self.ast_queue.put(ast)

    self.ast_queue_done = True

  def populate_ast_attributes(self):
    """Calls all the methods to populate each AST list for each site type.
    Uses self.ast_queue to get ASTs. Multithreaded, calls each populate_ast_<site_type> method.
    
    Args:
      None
    
    Returns:
      None
    """
    print("STARTED populate_ast_attributes thread")
    while(not (self.ast_queue.empty() and self.ast_queue_done)):
      ast = self.ast_queue.get()
      self.ast_queue.task_done()
      
      threads = []

      if(self.parse_single_cwe == 'buffer_write' 
        or self.parse_single_cwe == 'all'):
        threads.append( threading.Thread(None, 
          target=self.populate_ast_buffer_writes, args=(ast,)) )
      
      if(self.parse_single_cwe == 'buffer_read' 
        or self.parse_single_cwe == 'all'):
        threads.append( threading.Thread(None, 
          target=self.populate_ast_buffer_reads, args=(ast,)) )

      for thread in threads:
        thread.start()

      for thread in threads:
        thread.join()

  def populate_ast_buffer_writes(self, ast):
    """Calls pycparser node visitor in the ast. puts the buffer write
    nodes in the ast_buffer_writes queue.

    Notes: Adds tuple (node, source_line) to self.ast_buffer_writes

    Args:
      ast (c_ast): AST with source to be searched for sites

    Return:
      None
    """
    buffer_write_visitor = buffer_write.BufferWriteVisitor()
    buffer_write_visitor.visit(ast[2])
    sourceText = ast[1].split('\n')
    for node in buffer_write_visitor.nodes:
      self.ast_buffer_writes.put((node, sourceText[node.coord.line-1].strip()))

  def populate_ast_buffer_reads(self, ast):
    """Calls pycparser node visitor in the ast. puts the buffer reads
    nodes in the ast_buffer_reads queue.

    Notes: Adds tuple (node, source_line) to self.ast_buffer_reads

    Args:
      ast (c_ast): AST with source to be searched for sites

    Return:
      None
    """
    buffer_read_visitor = buffer_read.BufferReadVisitor()
    buffer_read_visitor.visit(ast[2])
    sourceText = ast[1].split('\n')
    for node in buffer_read_visitor.nodes:
      self.ast_buffer_reads.put((node, sourceText[node.coord.line-1].strip()))
