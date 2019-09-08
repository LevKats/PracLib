from setuptools import setup, find_packages

setup(name='prac_code',
      version='0.1',
      description='It can help in your homework',
      long_description="It's joke.",
      keywords='funniest joke comedy flying circus',
      author='Lev Kats',
      packages=find_packages(),
      install_requires=[
          'sympy', 'matplotlib', 'numpy', 'scipy', 'pandas'
      ],
      include_package_data=True,
      zip_safe=False)
