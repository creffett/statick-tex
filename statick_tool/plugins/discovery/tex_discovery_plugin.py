"""Discover TeX files to analyze."""

from __future__ import print_function

import fnmatch
import os
import subprocess
from collections import OrderedDict

from statick_tool.discovery_plugin import DiscoveryPlugin


class TexDiscoveryPlugin(DiscoveryPlugin):
    """Discover TeX files to analyze."""

    def get_name(self):
        """Get name of discovery type."""
        return "tex"

    def scan(self, package, level, exceptions=None):  # pylint: disable=too-many-locals
        """Scan package looking for TeX files."""
        tex_files = []
        globs = ["*.tex"]

        file_cmd_exists = True
        if not DiscoveryPlugin.file_command_exists():
            file_cmd_exists = False

        root = ''
        files = []
        for root, _, files in os.walk(package.path):
            for glob in globs:
                for f in fnmatch.filter(files, glob):
                    full_path = os.path.join(root, f)
                    tex_files.append(os.path.abspath(full_path))

            if file_cmd_exists:
                for f in files:
                    full_path = os.path.join(root, f)
                    output = subprocess.check_output(["file", full_path],
                                                     universal_newlines=True)
                    if f.endswith('.sty') or f.endswith('.log') or \
                            f.endswith('.cls'):
                        continue
                    # pylint: disable=unsupported-membership-test
                    if "LaTeX document" in output or \
                            "BibTeX text file" in output or \
                            "LaTeX 2e document" in output:
                        # pylint: enable=unsupported-membership-test
                        tex_files.append(os.path.abspath(full_path))

        tex_files = list(OrderedDict.fromkeys(tex_files))

        print("  {} TeX files found.".format(len(tex_files)))
        if exceptions:
            original_file_count = len(tex_files)
            tex_files = exceptions.filter_file_exceptions_early(package, tex_files)
            if original_file_count > len(tex_files):
                print("  After filtering, {} TeX files will be scanned.".format(len(tex_files)))

        package["tex"] = tex_files
