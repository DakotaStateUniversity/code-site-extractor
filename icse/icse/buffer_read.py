"""Node Visitor for buffer read sites.
Buffer read sites include buffer over reads and buffer under reads
"""

from pycparser import c_ast

class BufferReadVisitor(c_ast.NodeVisitor):
  """pyparser NodeVisitor for buffer read sites."""

  def __init__(self):
    """Constructor method with a list to keep the nodes that matches the site
    type and a node to keep track of the current node's parent.
    """
    self.nodes = []
    self.current_parent = None

  def visit_UnaryOp(self, node):
    """Rules for site matching."""

    if(not(isinstance(self.current_parent, c_ast.Assignment) and (self.current_parent.lvalue == node))):
      if(node.op == '*'):
        self.nodes.append(node.expr)

    self.current_parent = node
    for c_name, c in node.children():
      self.visit(c)

  def visit_ArrayRef(self, node):
    """Rules for site matching."""
    if(not(isinstance(self.current_parent, c_ast.Assignment) and (self.current_parent.lvalue == node))):
      if(not(isinstance(self.current_parent, c_ast.UnaryOp) and self.current_parent.op == '&')):
        self.nodes.append(node.name)

    self.current_parent = node
    for c_name, c in node.children():
      self.visit(c)

  '''
  def visit_FuncCall(self, node):
    """Rules for site matching."""
    if(isinstance(node.name, c_ast.ID)):
      if(node.name.name == 'SNPRINTF' or
          node.name.name == 'snprintf' or
          node.name.name == '_snprintf' or
          node.name.name == '_snwprintf' or
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
          node.name.name == 'wcpncpy'
          ):
        if(not isinstance(node.args.exprs[1], c_ast.Constant)):
          self.nodes.append(node.args.exprs[1])

      if(node.name.name == 'strlen' or node.name.name == 'wcslen'):
        self.nodes.append(node.args.exprs[0])

      if(node.name.name == 'fgets'):
        self.nodes.append(node.args.exprs[2])

      # include these fns if arg is a variable or a cast (not fn call or const)
      if((node.name.name == 'printLine' or node.name.name == 'printIntLine' or node.name.name == 'printLongLine' or node.name.name == 'printLongLongLine' or node.name.name == 'printHexCharLine' or node.name.name == 'printWLine') and (isinstance(node.args.exprs[0], c_ast.ID) or isinstance(node.args.exprs[0], c_ast.Cast))):
        self.nodes.append(node.args.exprs[0])

    self.current_parent = node
    for c_name, c in node.children():
      self.visit(c)
  '''

  def generic_visit(self, node):
    """Overwriting generic_visit to keep track of parent node."""
    self.current_parent = node
    for c_name, c in node.children():
      self.visit(c)

