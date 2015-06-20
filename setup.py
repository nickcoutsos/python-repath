from setuptools import setup

setup(
    name='repath',
    version='0.8.0',
    url='https://github.com/nickcoutsos/python-repath',
    author='Nikolaos Coutsos',
    author_email='ncoutsos@gmail.com',
    description='Generate regular expressions form ExpressJS path patterns',
    long_description=(
        'A port of the pathToRegexp node module to Python. '
        'Parses express-style paths to PCRE regular expression patterns, '
        'taking advantage of Python\'s named capture groups.'
    ),
    install_requires=[
        "six==1.9.0",
    ],
    packages=[],
    py_modules=['repath'],
    keywords='url path pattern regex express route',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
