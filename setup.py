from setuptools import setup, find_packages

setup(
    name="ccl-omnia",
    version="0.3.0",
    description="CCL OMNIA — AI-Native Terminal Operating System",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="MacJezzl",
    author_email="macjezzl@capechainlabs.io",
    url="https://github.com/MacJezzl1/CCL-0.1",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "flask>=3.0",
        "requests>=2.28",
        "psutil>=5.9",
    ],
    entry_points={
        "console_scripts": [
            "ccl=core.ccl_terminal:run_terminal",
            "ccl-dashboard=ccl_dashboard_server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Shells",
        "Topic :: Terminals",
    ],
)
