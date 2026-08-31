import os
from setuptools import setup, find_packages

try:
    from Cython.Build import cythonize
    ext_modules = cythonize(
        ["src/graphin/agents/scheduler_cy.pyx", "src/graphin/cordis/cython_speedup.pyx"],
        compiler_directives={"language_level": "3"}
    )
except ImportError:
    ext_modules = []


setup(
    name="graphin",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    ext_modules=ext_modules,
)
