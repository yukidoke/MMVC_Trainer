from setuptools import Extension, setup
from Cython.Build import cythonize
import numpy


extensions = [
    Extension(
        name="monotonic_align.core",
        sources=["core.pyx"],
        include_dirs=[numpy.get_include()],
    )
]


setup(
    name="mmvc-monotonic-align",
    ext_modules=cythonize(
        extensions,
        language_level=3,
    ),
)