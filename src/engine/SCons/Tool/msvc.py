"""engine.SCons.Tool.msvc

Tool-specific initialization for Microsoft Visual C/C++.

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

import os.path
import re
import string
import sys

import SCons.Action
import SCons.Builder
import SCons.Errors
import SCons.Platform.win32
import SCons.Tool
import SCons.Tool.msvs
import SCons.Util
import SCons.Warnings
import SCons.Scanner.RC

from MSVCCommon import merge_default_version, detect_msvs, set_psdk

CSuffixes = ['.c', '.C']
CXXSuffixes = ['.cc', '.cpp', '.cxx', '.c++', '.C++']

def validate_vars(env):
    """Validate the PCH and PCHSTOP construction variables."""
    if env.has_key('PCH') and env['PCH']:
        if not env.has_key('PCHSTOP'):
            raise SCons.Errors.UserError, "The PCHSTOP construction must be defined if PCH is defined."
        if not SCons.Util.is_String(env['PCHSTOP']):
            raise SCons.Errors.UserError, "The PCHSTOP construction variable must be a string: %r"%env['PCHSTOP']

def pch_emitter(target, source, env):
    """Adds the object file target."""

    validate_vars(env)

    pch = None
    obj = None

    for t in target:
        if SCons.Util.splitext(str(t))[1] == '.pch':
            pch = t
        if SCons.Util.splitext(str(t))[1] == '.obj':
            obj = t

    if not obj:
        obj = SCons.Util.splitext(str(pch))[0]+'.obj'

    target = [pch, obj] # pch must be first, and obj second for the PCHCOM to work

    return (target, source)

def object_emitter(target, source, env, parent_emitter):
    """Sets up the PCH dependencies for an object file."""

    validate_vars(env)

    parent_emitter(target, source, env)

    if env.has_key('PCH') and env['PCH']:
        env.Depends(target, env['PCH'])

    return (target, source)

def static_object_emitter(target, source, env):
    return object_emitter(target, source, env,
                          SCons.Defaults.StaticObjectEmitter)

def shared_object_emitter(target, source, env):
    return object_emitter(target, source, env,
                          SCons.Defaults.SharedObjectEmitter)

pch_action = SCons.Action.Action('$PCHCOM', '$PCHCOMSTR')
pch_builder = SCons.Builder.Builder(action=pch_action, suffix='.pch',
                                    emitter=pch_emitter,
                                    source_scanner=SCons.Tool.SourceFileScanner)


# Logic to build .rc files into .res files (resource files)
res_scanner = SCons.Scanner.RC.RCScan()
res_action  = SCons.Action.Action('$RCCOM', '$RCCOMSTR')
res_builder = SCons.Builder.Builder(action=res_action,
                                    src_suffix='.rc',
                                    suffix='.res',
                                    src_builder=[],
                                    source_scanner=res_scanner)


def generate(env):
    """Add Builders and construction variables for MSVC++ to an Environment."""
    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)

    for suffix in CSuffixes:
        static_obj.add_action(suffix, SCons.Defaults.CAction)
        shared_obj.add_action(suffix, SCons.Defaults.ShCAction)
        static_obj.add_emitter(suffix, static_object_emitter)
        shared_obj.add_emitter(suffix, shared_object_emitter)

    for suffix in CXXSuffixes:
        static_obj.add_action(suffix, SCons.Defaults.CXXAction)
        shared_obj.add_action(suffix, SCons.Defaults.ShCXXAction)
        static_obj.add_emitter(suffix, static_object_emitter)
        shared_obj.add_emitter(suffix, shared_object_emitter)

    env['CCPDBFLAGS'] = SCons.Util.CLVar(['${(PDB and "/Z7") or ""}'])
    env['CCPCHFLAGS'] = SCons.Util.CLVar(['${(PCH and "/Yu%s /Fp%s"%(PCHSTOP or "",File(PCH))) or ""}'])
    env['_CCCOMCOM']  = '$CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS $CCPCHFLAGS $CCPDBFLAGS'
    env['CC']         = 'cl'
    env['CCFLAGS']    = SCons.Util.CLVar('/nologo')
    env['CFLAGS']     = SCons.Util.CLVar('')
    env['CCCOM']      = '$CC /Fo$TARGET /c $SOURCES $CFLAGS $CCFLAGS $_CCCOMCOM'
    env['SHCC']       = '$CC'
    env['SHCCFLAGS']  = SCons.Util.CLVar('$CCFLAGS')
    env['SHCFLAGS']   = SCons.Util.CLVar('$CFLAGS')
    env['SHCCCOM']    = '$SHCC /Fo$TARGET /c $SOURCES $SHCFLAGS $SHCCFLAGS $_CCCOMCOM'
    env['CXX']        = '$CC'
    env['CXXFLAGS']   = SCons.Util.CLVar('$CCFLAGS $( /TP $)')
    env['CXXCOM']     = '$CXX /Fo$TARGET /c $SOURCES $CXXFLAGS $CCFLAGS $_CCCOMCOM'
    env['SHCXX']      = '$CXX'
    env['SHCXXFLAGS'] = SCons.Util.CLVar('$CXXFLAGS')
    env['SHCXXCOM']   = '$SHCXX /Fo$TARGET /c $SOURCES $SHCXXFLAGS $SHCCFLAGS $_CCCOMCOM'
    env['CPPDEFPREFIX']  = '/D'
    env['CPPDEFSUFFIX']  = ''
    env['INCPREFIX']  = '/I'
    env['INCSUFFIX']  = ''
#    env.Append(OBJEMITTER = [static_object_emitter])
#    env.Append(SHOBJEMITTER = [shared_object_emitter])
    env['STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME'] = 1

    env['RC'] = 'rc'
    env['RCFLAGS'] = SCons.Util.CLVar('')
    env['RCSUFFIXES']=['.rc','.rc2']
    env['RCCOM'] = '$RC $_CPPDEFFLAGS $_CPPINCFLAGS $RCFLAGS /fo$TARGET $SOURCES'
    env['BUILDERS']['RES'] = res_builder
    env['OBJPREFIX']      = ''
    env['OBJSUFFIX']      = '.obj'
    env['SHOBJPREFIX']    = '$OBJPREFIX'
    env['SHOBJSUFFIX']    = '$OBJSUFFIX'

    # Set-up ms tools paths for default version
    merge_default_version(env)
    set_psdk(env)

    env['CFILESUFFIX'] = '.c'
    env['CXXFILESUFFIX'] = '.cc'

    env['PCHPDBFLAGS'] = SCons.Util.CLVar(['${(PDB and "/Yd") or ""}'])
    env['PCHCOM'] = '$CXX $CXXFLAGS $CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS /c $SOURCES /Fo${TARGETS[1]} /Yc$PCHSTOP /Fp${TARGETS[0]} $CCPDBFLAGS $PCHPDBFLAGS'
    env['BUILDERS']['PCH'] = pch_builder

    if not env.has_key('ENV'):
        env['ENV'] = {}
    if not env['ENV'].has_key('SystemRoot'):    # required for dlls in the winsxs folders
        env['ENV']['SystemRoot'] = SCons.Platform.win32.get_system_root()

def exists(env):
    return detect_msvs()
