from setuptools import setup, find_packages
import qosd

setup(
        name="qosd",
        version=qosd.VERSION,
        description=qosd.DESCRIPTION,
        author='Laurent Ghigonis',
        author_email='ooookiwi@gmail.com',
        url='https://github.com/looran/qosd/',
        license='BSD',
        packages=['.'],
        entry_points = {'console_scripts': ['qosd = qosd:main']},
)
