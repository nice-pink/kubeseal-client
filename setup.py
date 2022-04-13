import kubeseal_client

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='kubeseal_client',
    version='0.0.1',
    author='Raffael @ Nice Pink',
    author_email='r@nice.pink',
    description='Python kubeseal wrapper',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/nice-pink/kubeseal-client',
    project_urls = {
        "Bug Tracker": "https://github.com/nice-pink/kubeseal-client/issues"
    },
    license='MIT',
    packages=['kubeseal-client'],
    install_requires=[],
)