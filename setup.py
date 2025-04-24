from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="facebook-instagram-analytics",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Facebook & Instagram Analytics Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/facebook-instagram-analytics",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "python-dotenv>=1.0.0",
        "pandas>=1.5.0",
        "matplotlib>=3.6.0",
        "python-dateutil>=2.8.2",
        "gspread>=5.7.0",
        "oauth2client>=4.1.3",
        "google-api-python-client>=2.70.0",
    ],
    entry_points={
        "console_scripts": [
            "fb-ig-analytics=facebook_instagram_analytics.examples.run_analytics:main",
        ],
    },
)
