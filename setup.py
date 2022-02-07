from setuptools import setup, find_packages


with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="timeeval_hyperopt",
    version='0.1.0',
    packages=find_packages(),
    license='MIT',
    author='Phillip Wenig',
    author_email='phillip.wenig@hpi.de',
    description='Hyperopt for TimeEval Algorithms',
    install_requires=required,
    python_requires=">=3.8",
    zip_safe=False
)
