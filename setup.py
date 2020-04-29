import io

from setuptools import find_packages
from setuptools import setup

setup(
    name="quicksand",
    version="0.1.0",
    license="GPLv3",
    description="Who cares about servers",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask", "flask_restful"],
    extras_require={"test": ["pytest", "coverage"]},
)
