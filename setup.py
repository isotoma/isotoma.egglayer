from setuptools import setup, find_packages

version = '0.0.4'

setup(
    name = 'isotoma.egglayer',
    version = version,
    description = "Utility for packaging things as eggs without setuptools",
    long_description = open("README.rst").read() + "\n" + \
                       open("CHANGES.txt").read(),
    url = "http://pypi.python.org/pypi/isotoma.egglayer",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Software Distribution",
        "License :: OSI Approved :: Apache Software License",
    ],
    keywords = "egg builder packaging",
    author = "John Carr",
    author_email = "john.carr@isotoma.com",
    license="Apache Software License",
    packages = find_packages(exclude=['ez_setup']),
    namespace_packages = ['isotoma'],
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        'setuptools',
        'Jinja2',
    ],
)
