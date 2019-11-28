from setuptools import setup

setup(
    name='lineusmusic',
    version='0.1.3',
    packages=['lineusmusic'],
    url='https://www.line-us.com',
    license='MIT',
    author='Robert Poll',
    author_email='rob@line-us.com',
    description='The Python module for Line-us Music',
    install_requires=[
        'lineus>=0.1.16',
    ]
)
