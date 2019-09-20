#!/usr/bin/env python3.7
"""
imports
"""
# external modules
import subprocess
import os
import click
import time
import concurrent.futures

from multiprocessing import Pool
from functools import lru_cache
from typing import Generator

# internal modules
from repo_stats import RepoStatistics


def create_git_command(urls_list: list) -> Generator[str, None, None]:
    """
    For each repository from the list of repo urls
    produce a git clone command and return
    :params: list of urls
    :return: generator
    """
    for url in urls_list:
        yield f'git clone {url.decode("utf-8")}'


def generate_git_commands(filename: str) -> list:
    """
    read the file specified, then use python generators
    to map through the list of urls and for each url produce
    a git command for it, then convert the generator to list
    :params: filename
    :return: list of git clone commands
    """
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            try:
                lines = f.readlines()
                generator = create_git_command(lines) # creating and initializing a python generator
                git_commands = list(generator)
                git_commands.pop(0)
                return git_commands
            except Exception as e:
                print(e)


def process_command(command):
    """
    process bash commands
    :params: command, bash command
    """
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    if error is not None:
        return error
    if output:
        return output
    return None


@click.command()
@click.argument('threads')
@click.argument('filename')
def start_process(filename: str, threads: int):
    """
    run the process
    """
    t1 = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(int(threads)) as executor:
        executor.map(process_command, generate_git_commands(filename))
    t2 = time.perf_counter()

    print(f"Finished cloning in {t2-t1} second(s)")

@click.group()
def cli(): pass

if __name__ == "__main__":
    cli.add_command(start_process)
    cli()

