"""SCons.Tool.fortran

Tool-specific initialization for a generic Posix f77/f90 Fortran compiler.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

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

import re
import string

import SCons.Action
import SCons.Defaults
import SCons.Scanner.Fortran
import SCons.Tool
import SCons.Util
from SCons.Tool.FortranCommon import DialectAddToEnv

compilers = ['f95', 'f90', 'f77']

#
#  Not yet sure how to deal with fortran pre-processor functions.
#  Different compilers do this differently in modern fortran.  Some still
#  rely on the c pre-processor, some (like cvf, ivf) have their own
#  pre-processor technology and use intermediary suffixes (.i90)
#
FortranSuffixes = [".f", ".for", ".ftn", ]
FortranPPSuffixes = ['.fpp', '.FPP']

def add_to_env(env):
    """Add Builders and construction variables for Fortran to an Environment."""
    DialectAddToEnv(env, "FORTRAN", "F77", "_FORTRAND", FortranSuffixes,
                    FortranPPSuffixes, support_module = 1)

    env['FORTRANMODPREFIX'] = ''     # like $LIBPREFIX
    env['FORTRANMODSUFFIX'] = '.mod' # like $LIBSUFFIX

    env['FORTRANMODDIR'] = ''          # where the compiler should place .mod files
    env['FORTRANMODDIRPREFIX'] = ''    # some prefix to $FORTRANMODDIR - similar to $INCPREFIX
    env['FORTRANMODDIRSUFFIX'] = ''    # some suffix to $FORTRANMODDIR - similar to $INCSUFFIX
    env['_FORTRANMODFLAG'] = '$( ${_concat(FORTRANMODDIRPREFIX, FORTRANMODDIR, FORTRANMODDIRSUFFIX, __env__, RDirs)} $)'

def generate(env):
    import f77
    import f90
    import f95
    f77.add_to_env(env)
    f90.add_to_env(env)
    f95.add_to_env(env)

    add_to_env(env)

    env['_FORTRAND'] = env.Detect(compilers) or 'f77'

def exists(env):
    return env.Detect(compilers)
