import io
from setuptools import find_packages, setup

# with io.open("README.rst", "rt", encoding="utf8") as f:
#     readme = f.read()

setup(
    name="surveyor",
    version="0.0.1",
    license="LICENSE",
    maintainer="Bryant Cassidey",
    maintainer_email="tcassidey@crimson.ua.edu",
    description="Creates a flask app for behavioral experiments.",
    # long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask", "pandas", "numpy"],
    extras_require={"test": ["pytest", "coverage"]},
)
