## Installation

```bash
pip install git+https://github.com/season-framework/season-flask
# or
pip install season
```

## Usage

- create project

```bash
cd <workspace>
sf create your-project-name
```

- create your websrc

```bash
cd <your-project-path>
sf add module dashboard
sf add module theme --uri https://git.season.co.kr/season-flask/module-theme-tabler # theme for tabler ui
sf add filter testfilter
sf add model testset
```

- add repo

```bash
cd <your-project-path>
sf config --set repo --value https://git.season.co.kr/season-flask # git repo project root uri of your system
sf add module something  # git from https://git.season.co.kr/season-flask/something, if not exists build default
sf config --unset repo
```

- start

```bash
cd <your-project-path>
sf run
```