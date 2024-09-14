import glob
import subprocess
import os
import argparse
import sys

def get_filenames(paths: list[str], append_extension: str = "", directory: str = ".") -> list[str]:
    """
    Return an array of filenames given a list of path

    Automatically handles

    Can optionally append an extension (eg. ".ignore") to the paths
    """
    rv: list[str] = []

    for path in paths:
        path = path.strip()

        ## Skip empty and commented lines
        if path == "" or path[0] == "#":
            continue

        base, ext = os.path.splitext(path)

        if ext in [".rpy", ".rpyc", ".rpyb", ".rpymc"]:
            alternative_extensions = [".rpy", ".rpyc"]
        elif ext in [".py", ".pyc", ".pyo", ".pyi"]:
            alternative_extensions = [".py", ".pyc", ".pyo", ".pyi"]
        elif ext == '' and base[-1] in ['*', '?']:
            alternative_extensions = [".rpy", ".rpyc"] + [".py", ".pyc", ".pyo", ".pyi"]
        else:
            alternative_extensions = [ext]

        for ext in alternative_extensions:
            if append_extension:
                test_path = base + ext + append_extension
            else:
                test_path = base + ext

            files = glob.glob(test_path, recursive=True)
            rv += files


    return rv


def exclude_files(filelist, excluded_extension, run_git=True, project_directory="."):
    paths: list[str]

    with open(filelist, "r", encoding="UTF-8") as f:
        paths = f.read().replace("\r", "").split("\n")

    prev_cwd = os.getcwd()
    os.chdir(project_directory)

    fns = get_filenames(paths)

    print(f"Found {len(fns)} files")

    if len(fns) > 0 and run_git:
        # subprocess.run(["git", "update-index", "--skip-worktree"] + fns)

        for fn in fns:
            subprocess.run(["git", "update-index", "--skip-worktree", fn],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)

    for fn in fns:
        os.rename(fn, fn + excluded_extension)

    os.chdir(prev_cwd)

    print(f"Excluded {len(fns)} files")


def restore_files(filelist, excluded_extension, run_git=True, project_directory="."):
    paths: list[str]

    with open(filelist, "r", encoding="UTF-8") as f:
        paths = f.read().replace("\r", "").split("\n")

    prev_cwd = os.getcwd()
    os.chdir(project_directory)

    fns = get_filenames(paths, append_extension=excluded_extension)

    original_fns = []
    for fn in fns:
        original_fns.append(os.path.splitext(fn)[0])
        os.rename(fn, original_fns[-1])

    print(f"Found {len(fns)} files")

    if len(fns) > 0 and run_git:
        # subprocess.run(["git", "update-index", "--no-skip-worktree"] + original_fns)

        for fn in original_fns:
            subprocess.run(["git", "update-index", "--no-skip-worktree", fn],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)

    os.chdir(prev_cwd)

    print(f"Restored {len(original_fns)} files")


def main():
    parser = argparse.ArgumentParser(
        prog='modify_renpy_script_load.py',
        description="""Modifies which script files Ren'Py will load. This can improve (re)load times during development.
This is done by modifying the extension of the script filenames. We also instruct git to skip them in the worktree so that the scripts are not detected as changed.""",
        epilog="""Glob-like paths must be supplied in the filelist. For example:
-----------------
game/tl/**/*.rpy
# Comments are allowed
game/scripts/dir/*.rpy
game/scripts/heavy_script.rpy
-----------------

Specifying .rpy will automatically handle .rpyc, .rpyb, .rpymc
Specifying .py will automatically handle .pyc, .pyo, .pyi

If a wildcard is used at the end (eg. game/tl/*) then both Ren'Py and Python filetypes are handled.
""",
        formatter_class=argparse.RawTextHelpFormatter,
        )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("--exclude", "-e", metavar="filelist", type=str,
        help="Provide the path to a file that contains a list of all the scripts to exclude")

    group.add_argument("--restore", "-r", metavar="filelist", type=str,
        help="Provide the path to a file that contains a list of all the scripts to restore")

    parser.add_argument("--extension", "-x", metavar="ext", type=str, default=".ignore",
        help="The extension to add to script files to prevent them from being loaded. Defaults to '.ignore'")

    parser.add_argument("--projectdir", "-d", metavar="dir", type=str, default=".",
        help="The directory of the game project. Git commands are run here, and script paths are relative to this directory.")

    parser.add_argument("--no-git", "-ng", action="store_true",
        help="If given, `git update-index --[no]-skip-worktree` will not be run")


    ## Automatically show the help message if no arguments are given
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])

    if args.extension[0] != ".":
        args.extension = "." + args.extension

    if args.exclude:
        exclude_files(args.exclude, args.extension, not args.no_git, args.projectdir)
    else:
        restore_files(args.restore, args.extension, not args.no_git, args.projectdir)


if __name__ == "__main__":
    main()