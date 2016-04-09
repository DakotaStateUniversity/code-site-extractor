"""Site class file."""

class Site:
  """Representation of a site.
  """

  def __init__(
      self,
      filename,
      site_type,
      line,
      code,
      info=None,
      ):
    """Constructor for Site class:

    filename is the name of the file which contains the site.
    site_type is the representation string for the type of the possible bug,
    like buffer_overflow or div_by_zero.
    line is the line where the site is present in filename.
    code is the entire line where the site is.
    info is the variable causing the possible bug.
    """
    self.filename = filename
    self.site_type = site_type
    self.line = line
    self.code = code
    self.info = info
