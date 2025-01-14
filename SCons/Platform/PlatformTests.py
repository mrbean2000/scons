# MIT License
#
# Copyright The SCons Foundation
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

import collections
import unittest
import os

import SCons.compat
import SCons.Errors
import SCons.Platform
import SCons.Environment
import SCons.Action


class Environment(collections.UserDict):
    def Detect(self, cmd):
        return cmd

    def AppendENVPath(self, key, value) -> None:
        pass


class PlatformTestCase(unittest.TestCase):
    def test_Platform(self) -> None:
        """Test the Platform() function"""
        p = SCons.Platform.Platform('cygwin')
        assert str(p) == 'cygwin', p
        env = Environment()
        p(env)
        assert env['PROGSUFFIX'] == '.exe', env
        assert env['LIBSUFFIX'] == '.a', env
        assert env['SHELL'] == 'sh', env
        assert env['HOST_OS'] == 'cygwin', env
        assert env['HOST_ARCH'] != '', env

        p = SCons.Platform.Platform('os2')
        assert str(p) == 'os2', p
        env = Environment()
        p(env)
        assert env['PROGSUFFIX'] == '.exe', env
        assert env['LIBSUFFIX'] == '.lib', env
        assert env['HOST_OS'] == 'os2', env
        assert env['HOST_ARCH'] != '', env

        p = SCons.Platform.Platform('posix')
        assert str(p) == 'posix', p
        env = Environment()
        p(env)
        assert env['PROGSUFFIX'] == '', env
        assert env['LIBSUFFIX'] == '.a', env
        assert env['SHELL'] == 'sh', env
        assert env['HOST_OS'] == 'posix', env
        assert env['HOST_ARCH'] != '', env

        p = SCons.Platform.Platform('irix')
        assert str(p) == 'irix', p
        env = Environment()
        p(env)
        assert env['PROGSUFFIX'] == '', env
        assert env['LIBSUFFIX'] == '.a', env
        assert env['SHELL'] == 'sh', env
        assert env['HOST_OS'] == 'irix', env
        assert env['HOST_ARCH'] != '', env

        p = SCons.Platform.Platform('aix')
        assert str(p) == 'aix', p
        env = Environment()
        p(env)
        assert env['PROGSUFFIX'] == '', env
        assert env['LIBSUFFIX'] == '.a', env
        assert env['SHELL'] == 'sh', env
        assert env['HOST_OS'] == 'aix', env
        assert env['HOST_ARCH'] != '', env

        p = SCons.Platform.Platform('sunos')
        assert str(p) == 'sunos', p
        env = Environment()
        p(env)
        assert env['PROGSUFFIX'] == '', env
        assert env['LIBSUFFIX'] == '.a', env
        assert env['SHELL'] == 'sh', env
        assert env['HOST_OS'] == 'sunos', env
        assert env['HOST_ARCH'] != '', env

        p = SCons.Platform.Platform('hpux')
        assert str(p) == 'hpux', p
        env = Environment()
        p(env)
        assert env['PROGSUFFIX'] == '', env
        assert env['LIBSUFFIX'] == '.a', env
        assert env['SHELL'] == 'sh', env
        assert env['HOST_OS'] == 'hpux', env
        assert env['HOST_ARCH'] != '', env

        p = SCons.Platform.Platform('win32')
        assert str(p) == 'win32', p
        env = Environment()
        p(env)
        assert env['PROGSUFFIX'] == '.exe', env
        assert env['LIBSUFFIX'] == '.lib', env
        assert env['HOST_OS'] == 'win32', env
        assert env['HOST_ARCH'] != '', env

        exc_caught = None
        try:
            p = SCons.Platform.Platform('_does_not_exist_')
        except SCons.Errors.UserError:
            exc_caught = 1
        assert exc_caught, "did not catch expected UserError"

        env = Environment()
        SCons.Platform.Platform()(env)
        assert env != {}, env

    def test_win32_no_arch_shell_variables(self) -> None:
        """
        Test that a usable HOST_ARCH is available when
        neither: PROCESSOR_ARCHITEW6432 nor PROCESSOR_ARCHITECTURE
        is set for SCons.Platform.win32.get_architecture()
        """

        # Save values if defined
        PA_6432 = os.environ.get('PROCESSOR_ARCHITEW6432')
        PA = os.environ.get('PROCESSOR_ARCHITECTURE')
        if PA_6432:
            del(os.environ['PROCESSOR_ARCHITEW6432'])
        if PA:
            del(os.environ['PROCESSOR_ARCHITECTURE'])

        p = SCons.Platform.win32.get_architecture()

        # restore values
        if PA_6432:
            os.environ['PROCESSOR_ARCHITEW6432']=PA_6432
        if PA:
            os.environ['PROCESSOR_ARCHITECTURE']=PA

        assert p.arch != '', 'SCons.Platform.win32.get_architecture() not setting arch'
        assert p.synonyms != '', 'SCons.Platform.win32.get_architecture() not setting synonyms'


class TempFileMungeTestCase(unittest.TestCase):
    def test_MAXLINELENGTH(self) -> None:
        """ Test different values for MAXLINELENGTH with the same
            size command string to ensure that the temp file mechanism
            kicks in only at MAXLINELENGTH+1, or higher
        """
        # Init class with cmd, such that the fully expanded
        # string reads "a test command line".
        # Note, how we're using a command string here that is
        # actually longer than the substituted one. This is to ensure
        # that the TempFileMunge class internally really takes the
        # length of the expanded string into account.
        defined_cmd = "a $VERY $OVERSIMPLIFIED line"
        t = SCons.Platform.TempFileMunge(defined_cmd)
        env = SCons.Environment.SubstitutionEnvironment(tools=[])
        # Setting the line length high enough...
        env['MAXLINELENGTH'] = 1024
        env['VERY'] = 'test'
        env['OVERSIMPLIFIED'] = 'command'
        expanded_cmd = env.subst(defined_cmd)
        # Call the tempfile munger
        cmd = t(None, None, env, 0)
        assert cmd == defined_cmd, cmd
        # Let MAXLINELENGTH equal the string's length
        env['MAXLINELENGTH'] = len(expanded_cmd)
        cmd = t(None, None, env, 0)
        assert cmd == defined_cmd, cmd
        # Finally, let the actual tempfile mechanism kick in
        # Disable printing of actions...
        old_actions = SCons.Action.print_actions
        SCons.Action.print_actions = 0
        env['MAXLINELENGTH'] = len(expanded_cmd)-1
        cmd = t(None, None, env, 0)
        # ...and restoring its setting.
        SCons.Action.print_actions = old_actions
        assert cmd != defined_cmd, cmd

    def test_TEMPFILEARGJOINBYTE(self) -> None:
        """
        Test argument join byte TEMPFILEARGJOINBYTE
        """

        # Init class with cmd, such that the fully expanded
        # string reads "a test command line".
        # Note, how we're using a command string here that is
        # actually longer than the substituted one. This is to ensure
        # that the TempFileMunge class internally really takes the
        # length of the expanded string into account.
        defined_cmd = "a $VERY $OVERSIMPLIFIED line"
        t = SCons.Platform.TempFileMunge(defined_cmd)
        env = SCons.Environment.SubstitutionEnvironment(tools=[])
        # Setting the line length high enough...
        env['MAXLINELENGTH'] = 1024
        env['VERY'] = 'test'
        env['OVERSIMPLIFIED'] = 'command'
        env['TEMPFILEARGJOINBYTE'] = os.linesep
        expanded_cmd = env.subst(defined_cmd)

        # For tempfilemunge to operate.
        old_actions = SCons.Action.print_actions
        SCons.Action.print_actions = 0
        env['MAXLINELENGTH'] = len(expanded_cmd)-1
        cmd = t(None, None, env, 0)
        # print("CMD is:%s"%cmd)

        with open(cmd[-1],'rb') as f:
            file_content = f.read()
        # print("Content is:[%s]"%file_content)
        # ...and restoring its setting.
        SCons.Action.print_actions = old_actions
        assert file_content != env['TEMPFILEARGJOINBYTE'].join(['test','command','line'])

    def test_TEMPFILEARGESCFUNC(self) -> None:
        """
        Test a custom TEMPFILEARGESCFUNC
        """

        def _tempfile_arg_esc_func(arg):
            return str(arg).replace("line", "newarg")

        defined_cmd = "a $VERY $OVERSIMPLIFIED line"
        t = SCons.Platform.TempFileMunge(defined_cmd)
        env = SCons.Environment.SubstitutionEnvironment(tools=[])
        # Setting the line length high enough...
        env['MAXLINELENGTH'] = 5
        env['VERY'] = 'test'
        env['OVERSIMPLIFIED'] = 'command'

        # For tempfilemunge to operate.
        old_actions = SCons.Action.print_actions
        SCons.Action.print_actions = 0
        env['TEMPFILEARGESCFUNC'] = _tempfile_arg_esc_func
        cmd = t(None, None, env, 0)
        # print("CMD is: %s"%cmd)

        with open(cmd[-1], 'rb') as f:
            file_content = f.read()
        # print("Content is:[%s]"%file_content)
        # # ...and restoring its setting.
        SCons.Action.print_actions = old_actions
        assert b"newarg" in file_content

    def test_tempfilecreation_once(self) -> None:
        """
        Init class with cmd, such that the fully expanded
        string reads "a test command line".
        Note, how we're using a command string here that is
        actually longer than the substituted one. This is to ensure
        that the TempFileMunge class internally really takes the
        length of the expanded string into account.
        """
        defined_cmd = "a $VERY $OVERSIMPLIFIED line"
        t = SCons.Platform.TempFileMunge(defined_cmd)
        env = SCons.Environment.SubstitutionEnvironment(tools=[])
        # Setting the line length high enough...
        env['VERY'] = 'test'
        env['OVERSIMPLIFIED'] = 'command'
        expanded_cmd = env.subst(defined_cmd)
        env['MAXLINELENGTH'] = len(expanded_cmd)-1
        # Disable printing of actions...
        old_actions = SCons.Action.print_actions
        SCons.Action.print_actions = 0
        # Create an instance of object derived class to allow setattrb

        class Node:
            class Attrs:
                pass

            def __init__(self) -> None:
                self.attributes = self.Attrs()

        target = [Node()]
        cmd = t(target, None, env, 0)
        # ...and restoring its setting.
        SCons.Action.print_actions = old_actions
        assert cmd != defined_cmd, cmd
        assert cmd == target[0].attributes.tempfile_cmdlist[defined_cmd]



class PlatformEscapeTestCase(unittest.TestCase):
    def test_posix_escape(self) -> None:
        """  Check that paths with parens are escaped properly
        """
        import SCons.Platform.posix

        test_string = "/my (really) great code/main.cpp"
        output = SCons.Platform.posix.escape(test_string)

        # We expect the escape function to wrap the string
        # in quotes, but not escape any internal characters
        # in the test_string. (Parens doesn't require shell
        # escaping if their quoted)
        assert output[1:-1] == test_string


if __name__ == "__main__":
    unittest.main()


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
