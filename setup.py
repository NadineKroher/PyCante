from setuptools import setup, find_packages

import imp

setup(
    name='cante',
    version='1.0',
    description='Automatic transcription of flamenco singing.',
    author='Nadine Kroher',
    author_email='nkroher@us.es',
    url='http://www.cofla-project.com',
    #download_url='http://github.com/cante...',
    packages=find_packages(),
    long_description="""CANTE: An algorithm for automatic transcription of flamenco singing from polyphonic music recordings.""",
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
    ],
    keywords='audio flamenco MIR',
    #license='ISC',
    install_requires=[
        'numpy',
        'scipy',
    ],
    include_package_data=True,
)