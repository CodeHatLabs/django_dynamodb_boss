import os
from setuptools import setup, find_packages


setup(
    name='django_dynamodb_boss',
    version=0.0,
    author='Code Hat Labs, LLC',
    author_email='dev@codehatlabs.com',
    url='https://github.com/CodeHatLabs/django_dynamodb_boss',
    description='Django extensions for dynamodb_boss',
    packages=find_packages(),
    long_description="",
    keywords='python Django DynamoDB',
    zip_safe=False,
    install_requires=[
        'dynamodb_boss'
    ],
    test_suite='',
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
