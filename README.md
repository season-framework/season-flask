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
sf build --uri https://git.season.co.kr/outsourcing/nice-kyg-websrc
```

- import from directory

```bash
sf build --uri /home/user/project/websrc
```


# Release Note

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
