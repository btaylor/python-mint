from setuptools import setup, find_packages
 
setup(
    name='pymint',
    version='0.1.1',
    description='Python Mint API',
    author='Hisham Zarka',
    author_email='hzarka@gmail.com',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires = [
        "setuptools",
    ],
    zip_safe=True,
)
