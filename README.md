# smersh-cli ![](https://img.shields.io/github/last-commit/CMEPW/smersh-cli.svg) ![](https://img.shields.io/github/issues/CMEPW/smersh-cli.svg) 

**smersh-cli** is a command line client for the [SMERSH API](https://github.com/CMEPW/Smersh) fully written in Python. 
It is an easy to use interactive command line made with CRUD in mind.

# Usage

To run smersh-cli, you simply have to invoke the `main.py` script with your SMERSH API url has single argument:

```bash
python main.py <smersh api url>
```

You will then be asked to enter your credentials before having an interactive command line interface (see below for an 
example).

![Example of a smersh-cli session](img/example.png)

## Commands

smersh-cli implements every single builtin `cmd2` command (see the [cmd2 documentation](https://cmd2.readthedocs.io/en/latest/features/builtin_commands.html) 
for more information about these commands). However, please think twice before using commands like `py` or `ipy` because
you can easily break something.

In addition to these commands, smersh-cli implements the following ones:

* show
* use
* assign
* save
* delete
* exit

Please note that every command is documented. The documentation can be shown with the `help` command.

### Commands and contexts

Some commands require a 'context' to be used. This is the case for the `assign`, `save` and `delete` commands. A context 
is used to tell the program about which object the operation you want to perform refers to. To change the context you 
need to use the `use` command. You can see at any time which context is active thanks to the prompt of the interactive 
command line. In order to exit the active context, use the `exit` command (**warning**: every unsaved modification will 
be lost).

# Installation

## Via Docker

This project includes a Dockerfile that you can build with the following command:

```bash
cd <project folder>
docker build .
```

Once the image is built, you can simply run smersh-cli with the following command:

```bash
docker run -it <container id> <smersh api url>
```

## Manually

smersh-cli requires at least Python 3.5 because of the usage of typing (see[PEP 484](https://www.python.org/dev/peps/pep-0484/) 
for more information). However, we recommend Python 3.8 to avoid using a hack to get the project working (see [issue #12](https://github.com/CMEPW/smersh-cli/issues/12)). 
If you have an older Python version, you will need to upgrade as we won't support any version below 3.5.

smersh-cli also depends on the following libraries:
    * rich
    * cmd2
    * requests
    * dataclasses_json
    * pydantic

If you have `pip` installed you can use the following command to install all dependencies at once :

```bash
pip install -r requirements.txt
```

# License

This license has no yet been chosen. We will update this section when we know which license to use.