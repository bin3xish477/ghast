from setuptools import setup, find_packages

setup(
    name='ghast-scanner',
    version='1.6.8',
    packages=find_packages(),
    install_requires=[
        'iniconfig==2.0.0',
        'packaging==23.1',
        'pluggy==1.2.0',
        'pytest==7.4.0',
        'PyYAML==6.0',
    ],
    author='Alex Rodriguez',
    author_email='arodriguez99@protonmail.com',
    description='Analyze the security posture of your GitHub Action',
    url='https://github.com/bin3xish477/ghast',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
