from setuptools import setup

setup(
    name='naomi',
    url='https://github.com/shunjuu/Naomi',
    author='Kyrielight',
    packages=['naomi'],
    install_requires=[
        'ayumi @ git+https://github.com/shunjuu/Ayumi',
        'requests'
    ],
    version='0.1',
    license='MIT',
    description='Izumi Show Similarity Searcher.'
)
