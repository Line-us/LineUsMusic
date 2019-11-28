from setuptools import setup

# python setup.py sdist
# twine upload dist/*

setup(
    name='lineusmusic',
    version='1.0.0',
    packages=['lineusmusic'],
    url='https://github.com/Line-us/LineUsMusic',
    license='MIT',
    author='Robert Poll',
    author_email='rob@line-us.com',
    description='The Python module for Line-us Music',
    install_requires=[
        'lineus>=1.0.0',
    ]
)
