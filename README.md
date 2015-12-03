theodo-mugshot
==============

Transform any portrait picture into a theodo.fr compatible mugshot

INSTALL
-------

### Ubuntu

```
sudo apt-get install python-opencv
```

### Mac OS X

#### Python and virtualenv

Install python with brew

```
brew install python
```

Install virtualenv, create project envionement and install dependencies.

```
$ pip install virtualenv virtualenvwrapper
$ mkvirtualenv theodo-mugshot
$ pip install numpy
```

### Install opencv

```
$ brew tap homebrew/science
$ brew install opencv
```

Link your opencv libraries to your virtualenv

```
cp /usr/local/Cellar/opencv/2.4.12/lib/python2.7/site-packages/cv* ~/.virtualenvs/theodo-mugshot/lib/python2.7/site-packages/
```

## Run the project

```
./mugsotify my_image.jpg
```
