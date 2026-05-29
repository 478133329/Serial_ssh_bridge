#!/usr/bin/env python3

import sys
import platform
import os.path
import shutil
from setuptools import Extension, setup
from Cython.Build import cythonize

ek18_sources = [
    "ek18.pyx",
    "kermit.c",
    "helper.c",
]

sources = [os.path.join("ek18", i) for i in ek18_sources]
build_dir = "build/ext"
module_name = "ek18"


def main():
    argv = sys.argv[1:]
    if not argv:
        argv = ["build_ext"]

    print("argv:", argv)
    print("platform:", platform.platform())

    ext_modules = cythonize(
        [Extension(module_name, sources, include_dirs=[build_dir])],
        build_dir=build_dir,
        force=False,
        language_level=3,
        depfile=True,
    )

    r = setup(
        name=module_name,
        ext_modules=ext_modules,
        zip_safe=False,
        script_args=argv,
    )

    pyx_path = r.command_obj["build_ext"].get_outputs()[0]
    shutil.copy2(pyx_path, ".")


if __name__ == "__main__":
    main()
