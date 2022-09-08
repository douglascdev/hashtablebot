from setuptools import setup

with open("requirements.txt", "r") as file:
    requirements = file.read().splitlines()

setup(
    name='hashtablebot',
    version='0.1.0',
    packages=[
        'hashtablebot',
        'hashtablebot.entity',
        'hashtablebot.banking',
        'hashtablebot.persistence',
        'hashtablebot.memory_entity'
    ],
    url='',
    license='',
    author='douglascdev',
    author_email='',
    description='',
    entry_points={
        'console_scripts': [
            'hashtablebot = hashtablebot.main:main',
        ],
    },
    install_requires=requirements,
    extras_require={
        'dev': [
            'sphinx',
            'sphinx_rtd_theme',
        ]
    }
)
