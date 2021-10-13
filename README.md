# Installation

```bash
pip install git+https://github.com/season-framework/season-flask
# or
pip install season
```

# Usage

## Getting Started

- create project

```bash
cd <workspace>
sf create myapp
cd myapp
```

- create your websrc

```bash
sf module remove theme
sf module import theme --uri https://git.season.co.kr/season-flask/theme
```

- start development mode

```bash
sf run
```

## Import Exists Project from websrc

- import from git repo

```bash
sf build --uri https://github.com/season-framework/something
```

- import from directory

```bash
sf build --uri /home/user/project/websrc
```


# Release Note

### 0.3.6

- Socket.io disconnect bug fixed

### 0.3.3

- Socket.io Namespace Injection

### 0.3.2

- Socket.io bug fixed

### 0.3.1

- Socket.io bug fixed


### 0.3.0

- add Socket.io 


### 0.2.14

- add response.template_from_string function

### 0.2.13

- add response.template function

### 0.2.12

- add variable expression change option

### 0.2.11

- interface loader update


### 0.2.10

- config onerror changed 

### 0.2.9

- add response.abort

### 0.2.8

- error handler in controller `__error__`

### 0.2.7

- response redirect update (relative module path)

### 0.2.6

- logger upgrade (file trace bug fixed)

### 0.2.5

- logger upgrade (log executed file trace)

### 0.2.4

- logger upgrade (code trace)

### 0.2.3

- error handler bug fixed

### 0.2.2

- apache wsgi bug fixed (public/app.py)

### 0.2.1

- apache wsgi bug fixed

### 0.2.0

- framework structure upgraded
- command line tool function changed
- submodule structure added
- logging 
- simplify public directory structure
