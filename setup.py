from setuptools import setup, find_packages
import geyser

setup(name = "geyser",
      version = geyser.__version__,
      description = "Golang service compiler",
      url = "https://github.com/zheld/geyser",

      author = "Sergey Zheldokas",
      author_email = "sa.zheldokas@gmail.com",
      license = "MIT",

      classifiers = [
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 3 - Alpha',

          # Indicate who your project is intended for
          'Intended Audience :: Developers',

          # Pick your license as you wish (should match "license" above)
          'License :: OSI Approved :: MIT License',

          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.

          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      keywords = "golang service compiler",
      packages = find_packages(),

      install_requires = ["GitPython", "psycopg2-binary"],
      )
