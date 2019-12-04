from setuptools import setup
from setuptools.command.build_py import build_py
import os

class my_build_py(build_py):
    def build_package_data(self):
        """Copy data files into build directory"""
        for package, src_dir, build_dir, filenames in self.data_files:
            for filename in filenames:
                tfilename = os.path.basename(filename)
                target = os.path.join(build_dir, tfilename)
                self.mkpath(os.path.dirname(target))
                srcfile = os.path.join(src_dir, filename)
                outf, copied = self.copy_file(srcfile, target)
                srcfile = os.path.abspath(srcfile)
                if (copied and
                        srcfile in self.distribution.convert_2to3_doctests):
                    self.__doctests_2to3.append(outf)


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = "langtag",
    version = "0.1",
    author = "SIL International",
    author_email = "fonts@sil.org",
    description = "Language tag processing for langtags.json",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/silnrsi/langtags",
    cmdclass = {'build_py': my_build_py},
    packages = ["langtag"],
    package_dir = {'': 'lib'},
    package_data = {'langtag' : ['../../pub/langtags.json']},
    license = 'MIT',
    classifiers = [
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

