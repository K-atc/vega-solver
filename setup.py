from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

with open('requirements.txt') as f:
    install_requires = f.read().split('\n')

setup(
    name='vega-solver',
    version='0.1.0',
    description='All sat style yet another theorem solver',
    long_description=readme,
    long_description_content_type='text/x-rst',
    author='Tomori Nao (@K_atc)',
    author_email='shiftx1026@gmail.com',
    url='https://github.com/K-atc/vega-solver',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),

    install_requires=install_requires,

    entry_points={
        "console_scripts": [
            "vega = vega.app:main"
        ]
    },

    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ],
)