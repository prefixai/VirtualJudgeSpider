from distutils.core import setup
import setuptools


setup(name='VirtualJudgeSpider',
      version='0.4.3',
      description='Virtual Judge Spider',
      author='dian xu',
      author_email='xudian.cn@gmail.com',
      packages=['VirtualJudgeSpider','VirtualJudgeSpider/OJs'],
      install_requires=['beautifulsoup4', 'lxml','requests']
      )
