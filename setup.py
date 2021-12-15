from setuptools import setup, find_packages

setup(
    name='fmriprep-group-report',
    version='0.0.1',
    author='Dylan M. Nielson',
    author_email='dylan.nielson@gmail.com',
    description='Make consolidated group reports from fmriprep output.',
    url='https://github.com/nimh-comppsych/fmriprep-group-report',
    py_modules=find_packages(),
    install_requires=[
        'Click',
        'pybids>=0.14',
        'pandas',
        'numpy',
        'beautifulsoup4'
    ],
    entry_points={
        'console_scripts':[
        'fmriprepgr=fmriprepgr.reports:make_report'
        ]
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX",
    ]
)