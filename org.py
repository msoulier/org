#!/usr/bin/env python

import argparse
import orgparse
from orgparse.node import OrgEnv
import sys
import os.path
import os
import logging
import datetime

logging.basicConfig()
log = logging.getLogger('org')
log.setLevel(logging.INFO)

todo_keys = ['TODO', 'IN-PROGRESS']
done_keys = ['DONE', 'DEFERRED', 'CANCELLED', 'DELEGATED']
todos = {}
env = OrgEnv(todos=todo_keys, dones=done_keys, filename='<string>')

class ToDo(object):
    def __init__(self, headline, scheduled, path, state="TODO"):
        self.headline = headline
        self.scheduled = scheduled
        self.path = path
        self.state = state
        self.sig = self.state + self.headline

    def __str__(self):
        return "%s %s: %s" % (self.state, self.headline, self.path)

def walknode(node, path):
    for child in node.children:
        log.debug("walknode: %s", child)
        s = str(child)
        if child.todo:
            t = ToDo(child.heading, child.scheduled, path, state=child.todo)
            if t.sig in todos:
                log.warning("found a duplicate: %s", t)
                log.warning("    original: %s", todos[t.sig])
            else:
                todos[t.sig] = t
            log.debug("captured: %s", t)
        walknode(child, path)

def visit(root, files):
    log.debug("visit: found files: %s", files)
    for f in files:
        if f.endswith(".org"):
            path = os.path.join(root, f)
            with open(path, "r") as orgfile:
                log.debug("visit: opening %s", path)
                orgbuf = orgparse.loads(orgfile.read(), env=env)
                for node in orgbuf[1:]:
                    log.debug("visit: HEADING: %s", node.heading)
                    walknode(node, path)
                    

def walk(rootdir):
    for root, dirs, files in os.walk(rootdir):
        visit(root, files)

def options():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        dest="debug",
        help="Verbose logging")
    parser.add_argument(
        "root",
        help="The root of the org filesystem")
    args = parser.parse_args()

    if not args.root:
        parser.print_help()
        sys.exit(1)

    if args.debug:
        log.setLevel(logging.DEBUG)

    return args

def main():
    if len(sys.argv) > 1:
        args = options()
        rootdir = args.root
        if os.path.isdir(rootdir):
            walk(rootdir)
        else:
            sys.stderr.write("ERROR: not a directory: %s\n" % rootdir)
            sys.exit(1)

    else:
        sys.stderr.write("Usage: %s <root directory>\n" % sys.argv[0])
        sys.exit(1)

    # Now walk the todo list and organise it
    todos_undone = []
    todos_inprogress = []
    todos_done = []

    for sig, todo in todos.items():
        log.debug("looping on todo: %s", todo)
        if todo.state == "TODO":
            todos_undone.append(todo)
        elif todo.state == "IN-PROGRESS":
            todos_inprogress.append(todo)
        else:
            todos_done.append(todo)

    log.info("todo list size: %d", len(todos_undone))
    log.info("in-progress list size: %d", len(todos_inprogress))
    log.info("done list size: %d", len(todos_done))

    log.info("Undone items:")
    for todo in todos_undone:
        log.info("    %s %s", todo.state, todo.headline)

    log.info("In-progress items:")
    for todo in todos_inprogress:
        log.info("    %s %s", todo.state, todo.headline)

    #log.info("Done items:")
    #for todo in todos_done:
    #    log.info("    %s %s", todo.state, todo.headline)

if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        log.exception("ERROR: uncaught exception: %s", err)
        sys.exit(1)
