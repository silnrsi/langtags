import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "langtag",
    version = "0.1",
    author = "SIL International",
    author_email = "fonts@sil.org",
    description = "Language tag processing for langtags.json",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/silnrsi/langtags",
    packages = ["langtag"],
    package_dir = {'': 'lib'},
    scripts = ['bin/langtag'],
    license = 'MIT',
    classifiers = [
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

