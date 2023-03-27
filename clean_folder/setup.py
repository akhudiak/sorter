from setuptools import setup, find_namespace_packages

setup(
    name='clean',
    version='0.0.1',
    description='Sorting the contents of the folder',
    url='https://github.com/akhudiak/sorter',
    author='White Pepper',
    author_email='artem.khudiak@gmail.com',
    license='MIT',
    packages=find_namespace_packages(),
    entry_points={'console_scripts': ['clean-folder = clean_folder.clean:main']}
)