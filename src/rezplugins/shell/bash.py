"""
Bash shell
"""
import os
import os.path
from rez.shells import Shell
from rez.utils.platform_ import platform_
from rez.utils.data_utils import cached_class_property
from rezplugins.shell.sh import SH
from rez import module_root_path


class Bash(SH):
    rcfile_arg = '--rcfile'
    norc_arg = '--norc'

    @cached_class_property
    def executable(cls):
        return Shell.find_executable('bash')

    @classmethod
    def name(cls):
        return 'bash'

    @classmethod
    def startup_capabilities(cls, rcfile=False, norc=False, stdin=False,
                             command=False):
        if norc:
            cls._overruled_option('rcfile', 'norc', rcfile)
            rcfile = False
        if command is not None:
            cls._overruled_option('stdin', 'command', stdin)
            cls._overruled_option('rcfile', 'command', rcfile)
            stdin = False
            rcfile = False
        if stdin:
            cls._overruled_option('rcfile', 'stdin', rcfile)
            rcfile = False
        return (rcfile, norc, stdin, command)

    @classmethod
    def get_startup_sequence(cls, rcfile, norc, stdin, command):
        rcfile, norc, stdin, command = \
            cls.startup_capabilities(rcfile, norc, stdin, command)

        files = []
        envvar = None
        do_rcfile = False

        if (command is not None) or stdin:
            envvar = 'BASH_ENV'
            path = os.getenv(envvar)
            if path and os.path.isfile(os.path.expanduser(path)):
                files.append(path)
        elif rcfile or norc:
            do_rcfile = True
            if rcfile and os.path.exists(os.path.expanduser(rcfile)):
                files.append(rcfile)
        else:
            for file in (
                    "~/.bash_profile",
                    "~/.bash_login",
                    "~/.profile",
                    "~/.bashrc"):
                if os.path.exists(os.path.expanduser(file)):
                    files.append(file)

        return dict(
            stdin=stdin,
            command=command,
            do_rcfile=do_rcfile,
            envvar=envvar,
            files=files,
            bind_files=(
                "~/.bash_profile",
                "~/.bashrc"),
            source_bind_files=True
        )

    def _bind_interactive_rez(self):
        super(Bash, self)._bind_interactive_rez()
        completion = os.path.join(module_root_path, "completion", "complete.sh")
        self.source(completion)


def register_plugin():
    if platform_.name != "windows":
        return Bash
