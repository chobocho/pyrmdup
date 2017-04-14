from distutils.core import setup
import py2exe, sys, os

includes = [
"encodings",
"encodings.utf_8"
]

options = {
"bundle_files": 1,
"includes" : includes,
}
setup(
    options = {"py2exe": options},
    zipfile = None,
    console = [{'script':"pyrmdup.py"}],
)
