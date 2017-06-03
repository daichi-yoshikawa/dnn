dnn
===
Implementation of Deep Neural Network with numpy.
Less dependencies, easier to use.

# Get started
## Setup Python Virtual Environment
### Assumption
* Use python3
* Make directory for pyenv in "/home/<user-name>"
* Root directory of your python-workspace is in "/home/<user-name>/Workspace/python3_ws"
* "/home/<user-name>/Workspace/python3_ws/" is your working directory

### Setup procedure
* Install required packages
```
$ sudo apt-get install git gcc make openssl libssl-dev libbz2-dev libreadline-dev libsqlite3-dev
```
* Install pyenv
```
   $ cd ~
   $ git clone git://github.com/yyuu/pyenv.git ./pyenv
   $ mkdir -p ./pyenv/versions ./pyenv/shims
```
* Set paths
```
   $ echo 'export PYENV_ROOT="${HOME}/pyenv"' >> ~/.bashrc
   $ echo 'if [ -d "${PYENV_ROOT}" ]; then' >> ~/.bashrc
   $ echo '    export PATH=${PYENV_ROOT}/bin:$PATH' >> ~/.bashrc
   $ echo '    eval "$(pyenv init -)"' >> ~/.bashrc
   $ echo 'fi' >> ~/.bashrc
   $ exec $SHELL -l
   $ . ~/.bashrc
```
* Install pyenv-virtualenv
```
   $ cd $PYENV_ROOT/plugins
   $ git clone git://github.com/yyuu/pyenv-virtualenv.git
```
* Install python 3.5.2
```
   $ pyenv install 3.5.2
```
* Setup local pyenv
```
   $ mkdir -p ~/Workspace/python3_ws
   $ pyenv virtualenv 3.5.2 <name of this environment>
```
<name of this environment> can be like py352, python3_env, or anything you like.<br>
Here, it's assumed that you named the environment as "py352".
```
   $ pyenv local py352
   $ pip install --upgrade pip
```

## Install requisites
* python-3.5+ (Already installed)
* numpy
* matplotlib

Go to your virtual environment like /home/<user-name>/Workspace/python-2,
and do the follows.
```
pip install numpy
pip install matplotlib
```

# Example
## MNIST
* Run neural network for mnist.
```
cd <path-to-dnn>/examples/mnist
python -B mnist.py
```

