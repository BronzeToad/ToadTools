from setuptools import setup, find_packages

setup(
    name='my_package',  # Required
    version='0.1',  # Required
    description='A simple package for my reusable helper functions',  # Optional
    long_description=open('README.md').read(),  # Optional
    long_description_content_type='text/markdown',  # Optional
    url='https://github.com/yourusername/my_package',  # Optional
    author='Your Name',  # Optional
    author_email='your.email@example.com',  # Optional
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='helper functions, utilities',  # Optional
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required
    install_requires=['numpy'],  # Optional
    extras_require={  # Optional
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    package_data={  # Optional
        'my_package': ['data/*.dat'],
    },
    entry_points={  # Optional
        'console_scripts': [
            'my_package=my_package:main',
        ],
    },
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/yourusername/my_package/issues',
        'Source': 'https://github.com/yourusername/my_package/',
    },
)
