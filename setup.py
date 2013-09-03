try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


from distutils.core import setup
setup(name='skcmd',
      version='0.0.5',
      py_modules=['skcmd'],
      description='Command line interface to Skype',
long_description = file('README.md').read(),
author='Les Smithson',
      author_email='lsmithso@hare.demon.co.uk',
      url='http://www.github.com/lsmithso/skcmd',
      scripts = ['skcmd.py'],
      provides=['skcmd'],
      requires = ['skype4py'],


      )
