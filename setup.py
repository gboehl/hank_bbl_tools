from setuptools import setup, find_packages

setup(
        name = 'hank_bbl_tools',
        version = '0.0.1',
        author='Gregor Boehl',
        author_email='admin@gregorboehl.com',
        description='jl <-> py tools for HANK',
        packages = find_packages(),
        install_requires=[
            'numpy',
         ],
   )
