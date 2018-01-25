from setuptools import setup, find_packages

setup(
    name='asgard-api-plugin-metrics-example-1',
    version='0.1.0',

    description='a plugin to the Asgard API',
    long_description="Plugin",
    url='',
    author='',
    author_email='',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    entry_points={
        'asgard_api_metrics_mountpoint': [
            'init_ok = metrics:plugin_init_ok',
            'init_wrong_blueprint = metrics:plugin_init_wrong_return',
            'init_non_existant_entrypoint = metrics:does_not_exist',
            'init_exception_on_load = metrics:plugin_init_exception',
        ],
    },
)
