"""SCons.Scanner.D

Scanner for the Digital Mars "D" programming language.

Coded by Andy Friesen
17 Nov 2003

"""

#
# __COPYRIGHT__
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import string

import SCons.Scanner

def DScanner(fs = SCons.Node.FS.default_fs):
    """Return a prototype Scanner instance for scanning D source files"""
    ds = D(name = "DScanner",
           suffixes = '$DSUFFIXES',
           path_variable = 'DPATH',
           regex = 'import\s+([^\;]*)\;',
           fs = fs)
    return ds

class D(SCons.Scanner.Classic):
    def find_include(self, include, source_dir, path):
        if callable(path): path=path()
        # translate dots (package separators) to slashes
        inc = string.replace(include, '.', '/')

        i = SCons.Node.FS.find_file(inc + '.d', (source_dir,) + path)
        return i, include
