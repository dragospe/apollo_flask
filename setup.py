from setuptools import find_packages, setup

setup(
    name = 'apollo_flask',
    version = '0.1.0',
    author = "Peter Dragos",
    author_email = "pdragos@u.rochester.edu",
    description = "Webapp portion of the Apollo-AF project.",
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        'flask',
        'sqlalchemy',
        'rauth',
        'requests',
        'pytest',
        'python-dateutil',
        'gunicorn',
        'psycopg2-binary',
    ],
    classifiers = ["Programming Language :: Python :: 3"],
)
