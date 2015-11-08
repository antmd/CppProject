# vim: set expandtab:set ts=4:set sw=4
# This file is NOT licensed under the GPLv3, which is the license for the rest
# of YouCompleteMe.
#
# Here's the license text for this file:
#
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org/>

import sys
import os
import platform
import subprocess

osx_sdk = None
if getattr(platform, 'mac_ver'):
    (release, versioninfo, machine) = platform.mac_ver()
    os_ver = '.'.join(release.split('.')[0:2])
    script_path = os.path.dirname(__file__)
    osx_dev_dir = subprocess.check_output(['/usr/bin/xcode-select', '-p']).rstrip()
    osx_sdk = os.path.join(osx_dev_dir, 'Platforms', 'MacOSX.platform', 'Developer', 'SDKs', 'MacOSX{}.sdk'.format(os_ver))
    xcode_usr_base = os.path.join(osx_dev_dir, 'Toolchains', 'XcodeDefault', 'xctoolchain', 'usr')

common_flags = [
    '-fexceptions',
    '-arch', 'x86_64',
    '-DDEBUG=1',
    '-DUSE_CLANG_COMPLETER',
    '-I', script_path,
    '-I', './Headers',
]

objc_system_includes = [
    '-isysroot', osx_sdk,
    '-F', osx_sdk,
    '-F', os.path.join(script_path, 'Frameworks')
]

#isystem paths obtained with:
#    echo "int main(){}" | clang++ -v -fshow-source-location -std=c++0x -x c++ - 2>&1) | sed -n '/\<...\>/,/End of search/p' | grep '^ '
cpp_system_includes = [
    '-isysroot', osx_sdk,
    # Note, on OS X, Developer command-line tools must be installed via 'xcode-select install'
    '-isystem', '/usr/include',
    '-isystem', '/usr/local/include',
    '-isystem', os.path.join(script_path, 'external', 'include'),
]


cpp_specific_flags = [
    '-std=c++1y',
    '-stdlib=libc++',
    '-I', os.path.join(script_path,'include'),
    '-I', './include/ide'
]

#'-Wc++98-compat',
common_warning_flags = [
    '-Wall',
    '-Wextra',
    '-Werror',
    '-Wno-long-long',
    '-Wno-variadic-macros',
    '-Wno-unused',
    '-Wno-deprecated-declarations',
    '-Wno-unused-parameter',
]

'''
FLAG-SETS FOR COMPILATION

'''

# These are the compilation flags that will be used in case there's no
# compilation database set (by default, one is not set).
# CHANGE THIS LIST OF FLAGS. YES, THIS IS THE DROID YOU HAVE BEEN LOOKING FOR.
objc_flags = [
    '-mmacosx-version-min=10.8',
    '-fobjc-arc',
    '-ObjC',
    '-isystem', '/System/Library/Frameworks/Python.framework/Headers',
]
objc_flags.extend(objc_system_includes)
objc_flags.extend(common_warning_flags)
objc_flags.extend(common_flags)



cpp_flags = [
    '-fexceptions',
    '-x', 'c++',
]
cpp_flags.extend(cpp_system_includes)
cpp_flags.extend(cpp_specific_flags)
cpp_flags.extend(common_warning_flags)
cpp_flags.extend(common_flags)

objcpp_flags = [ '-x','objective-c++' ]
objcpp_flags.extend(objc_flags)
objcpp_flags.extend(cpp_specific_flags)
objcpp_flags.extend(cpp_system_includes)

extension_to_flags = {
    '.cpp': cpp_flags,
    '.cxx': cpp_flags,
    '.cc': cpp_flags,
    '.c': cpp_flags,
    '.m': objc_flags,
    '.mm': objcpp_flags
}


# Set this to the absolute path to the folder (NOT the file!) containing the
# compile_commands.json file to use that instead of 'flags'. See here for
# more details: http://clang.llvm.org/docs/JSONCompilationDatabase.html
#
# Most projects will NOT need to set this to anything; you can just change the
# 'flags' list of compilation flags. Notice that YCM itself uses that approach.
compilation_database_folder = ''

'''
if os.path.exists(compilation_database_folder):
    database = ycm_core.CompilationDatabase(compilation_database_folder)
else:
    database = None
'''
database = None

SOURCE_EXTENSIONS = ['.cpp', '.cxx', '.cc', '.c', '.m', '.mm']

def DirectoryOfThisScript():
    return os.path.dirname(os.path.abspath(__file__))


def MakeRelativePathsInFlagsAbsolute(flags, working_directory):
    if not working_directory:
        return list(flags)
    new_flags = []
    make_next_absolute = False
    path_flags = ['-isystem', '-I', '-iquote', '--sysroot=']
    for flag in flags:
        new_flag = flag

        if make_next_absolute:
            make_next_absolute = False
            if not flag.startswith('/'):
                new_flag = os.path.join(working_directory, flag)

        for path_flag in path_flags:
            if flag == path_flag:
                make_next_absolute = True
                break

            if flag.startswith(path_flag):
                path = flag[len(path_flag):]
                new_flag = path_flag + os.path.join(working_directory, path)
                break

        if new_flag:
            new_flags.append(new_flag)
    return new_flags


def IsHeaderFile(filename):
    extension = os.path.splitext(filename)[1]
    return extension in ['.h', '.hxx', '.hpp', '.hh']


def GetCompilationInfoForFile(filename):
    # The compilation_commands.json file generated by CMake does not have entries
    # for header files. So we do our best by asking the db for flags for a
    # corresponding source file, if any. If one exists, the flags for that file
    # should be good enough.
    if IsHeaderFile(filename):
        basename = os.path.splitext(filename)[0]
        for extension in SOURCE_EXTENSIONS:
            replacement_file = basename + extension
            if os.path.exists(replacement_file):
                compilation_info = database.GetCompilationInfoForFile(
                    replacement_file)
                if compilation_info.compiler_flags_:
                    return compilation_info
        return None
    return database.GetCompilationInfoForFile(filename)


def FlagsForFile(filename, **kwargs):
    if database:
        # Compilation database
        #
        # Bear in mind that compilation_info.compiler_flags_ does NOT return a
        # python list, but a "list-like" StringVec object
        compilation_info = GetCompilationInfoForFile(filename)
        if not compilation_info:
            return None

        final_flags = MakeRelativePathsInFlagsAbsolute(
            compilation_info.compiler_flags_,
            compilation_info.compiler_working_dir_)

    else:
        # No compilation database -- use the flags from this file
        #
        relative_to = DirectoryOfThisScript()
        src_ext = os.path.splitext(filename)[1]
        final_flags = MakeRelativePathsInFlagsAbsolute(extension_to_flags.get(src_ext,cpp_flags), relative_to)

    return {
        'flags': final_flags,
        'do_cache': True
    }
