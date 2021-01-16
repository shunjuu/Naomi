from setuptools import setup

setup(
    name='naomi',
    url='https://github.com/shunjuu/Naomi',
    author='Kyrielight',
    packages=['naomi'],
    install_requires=[
        "ayumi @ git+git://github.com/shunjuu/Ayumi@master#egg=ayumi",
        'requests'
    ],
    version='0.2',
    license='MIT',
    description='Izumi Show Similarity Searcher.'
)
