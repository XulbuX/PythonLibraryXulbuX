from mypyc.build import mypycify
from setuptools import setup
import os


def find_python_files(directory: str) -> list[str]:
    python_files: list[str] = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


source_files = find_python_files("src/xulbux")

setup(
    name="xulbux",
    ext_modules=mypycify(source_files),
)
