"""Node Visitor for buffer write sites.

Buffer write sites include stack and heap based buffer overflows and buffer
under writes.
"""

from pycparser import c_ast

class BufferWriteVisitor(c_ast.NodeVisitor):
  """pycparser NodeVisitor for buffer write sites."""

  def __init__(self):
    """Constructor method with a list to keep the nodes that matches the site
    type.
    """
    self.nodes = []

  def visit_Assignment(self, node):
    """Rules for site matching. '*ptr = 85;' or 'ptr[2] = 23;'"""
    if(isinstance(node.lvalue, c_ast.ArrayRef)):
      self.nodes.append(node)

    elif(isinstance(node.lvalue, c_ast.UnaryOp) and node.lvalue.op == '*'):
      self.nodes.append(node)

    for c_name, c in node.children():
      self.visit(c)

'''
  ### TODO add option to allow analyst to specify function & arguments that
  ###   lead to site ###
  def visit_FuncCall(self, node):
    """Rules for site matching."""
    #print node.name.name + '\n\n'
    if(isinstance(node.name, c_ast.ID)):
      if(node.name.name == 'fgets' or
          node.name.name == 'strcpy' or
          node.name.name == 'strncpy' or
          node.name.name == 'strncat' or
          node.name.name == 'strcat' or
          node.name.name == 'wcsncpy' or
          node.name.name == 'wcscpy' or
          node.name.name == 'wcsncat' or
          node.name.name == 'wcscat' or
          node.name.name == 'memset' or
          node.name.name == 'wmemset' or
          node.name.name == 'wcpcpy' or
          node.name.name == 'memcpy' or
          node.name.name == 'memmove' or
          node.name.name == 'wcpncpy' or
          node.name.name == 'snprintf' or
          node.name.name == '_snprintf' or
          node.name.name == '_snwprintf' or
          node.name.name == 'SNPRINTF'
          ):
        self.nodes.append(node.args.exprs[0])

      elif(node.name.name == 'fscanf'):
        self.nodes.append(node.args.exprs[2])

    for c_name, c in node.children():
      self.visit(c)
'''
