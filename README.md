# Ren'Py Modify Script Load
Modifies which script files Ren'Py will load. This can improve (re)load times during development.

This is done by modifying the extension of the script filenames. We also instruct git to skip them in the worktree so that the scripts are not detected as changed.

Good candidates to exclude to improve load times are:
- Translation files (can also be handled by [`config.defer_tl_scripts`](https://www.renpy.org/doc/html/translation.html#deferred-translation-loading))
- Scripts for scenes you are not currently modifying
- Special screens (eg. gallery)
- Files with long `init python` blocks

## Description
On larger Ren'Py projects, it can take a lot of time to load and reload the game. This can make it tedious to test changes quickly.

As part of the [lifecycle of a Ren'Py game](https://www.renpy.org/doc/html/lifecycle.html), the engine reads every single `.rpy` and `_ren.py` file in your game from scratch whenever you (re)load the game. This can lead to slow down since it's processing content from parts of the game that you may not be working on at the moment.

To speed up loading, this script will ignore selected `.rpy` script files by changing their extension so the Ren'py engine will not read them. We can also tell the version control software (in this case git) to ignore that the file was renamed using the [--skip-worktree flag in `git update-index`](https://git-scm.com/docs/git-update-index).

## Usage
Make sure to add `*.ignore` (or whatever you choose with the `--extension` argument) to your `.gitignore` file.

```bash
python3 main.py [ options... ]
```

**Arguments**

> --help

Displays a help messages with all the commands available.

> --exclude \<filelist>

Provide the path to a file that contains a list of all the scripts to exclude

> --restore \<filelist>

Provide the path to a file that contains a list of all the scripts to restore

> --extension \<ext>

The extension to add to script files to prevent them from being loaded. Defaults to '.ignore'

> --projectdir \<dir>

The directory of the game project. Git commands are run here, and script paths are relative to this directory.

> --no-git

If given, `git update-index --[no]-skip-worktree` will not be run

## Filelists

To specify which scripts to exclude, make use of [glob](https://docs.python.org/3/library/glob.html) strings. The `**` wildcard works recursively.

An example of a filelist is shown below. More examples can be found in the `filelist` folder:
```
game/tl/**/*.rpy

# Comments are allowed
game/scripts/dir/*.rpy
game/scripts/heavy_script.rpy
```

- Specifying `.rpy` will automatically handle `.rpyc`, `.rpyb`, and `.rpymc`
- Specifying `.py` will automatically handle `.pyc`, `.pyo`, and `.pyi`
- If a wildcard is used at the end (eg. game/tl/*) then both Ren'Py and Python scripts will be handled.

## Possible Issues
An exception will be thrown if the game tries to access a variable, function, or class in one of the excluded scripts.

To get around this, either:
1) Restore files, remove the line corresponding to the script in from the filelist, then exclude files again; or
2) Move the definition to a different file that you will not exclude

## Acknowledgements
Thanks to [MiiNiPaa](https://github.com/MiiNiPaa) for the idea ([Source](https://github.com/renpy/renpy/issues/5777#issuecomment-2348404822))