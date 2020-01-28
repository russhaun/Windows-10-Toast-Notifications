from pathlib import Path
from setuptools import setup

def from_here(relative_path):
    return Path(__file__).resolve().parent.joinpath(relative_path)

install_requires = ['pywin32']

extras_require = {'pillow': ['Pillow']}

setup(
    name='win10toast',
    version='0.9',
    install_requires=install_requires,
    extras_require=extras_require,
    packages=['win10toast'],
    license='MIT',
    url='https://github.com/nuno-andre/Windows-10-Toast-Notifications',
    download_url='https://github.com/nuno-andre/Windows-10-Toast-Notifications/archive/master.zip',
    description=(
        'An easy-to-use Python library for displaying '
        'Windows 10 Toast Notifications'
    ),
    include_package_data=True,
    package_data={
        '': ['*.txt'],
        'win10toast': ['data/*.ico'],
    },
    package_dir={'': 'src'},
    long_description=from_here('README.md').read_text(),
    long_description_content_type='text/markdown',
    author='Jithu R Jacob',
    author_email='jithurjacob@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'Operating System :: Microsoft',
        'Environment :: Win32 (MS Windows)',
        'License :: OSI Approved :: MIT License',
    ],
)
