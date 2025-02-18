#!/usr/bin/env python

import orgparse
import sys
import os.path
import os
import logging

logging.basicConfig()
log = logging.getLogger('org')
log.setLevel(logging.DEBUG)

todos = []

class ToDo(object):
    def __init__(self, headline, scheduled, path, state="TODO"):
        self.headline = headline
        self.scheduled = scheduled
        self.path = path
        self.state = state

    def __str__(self):
        return "%s %s" % (self.state, self.headline)

def walknode(node, path):
    for child in node.children:
        log.debug("walknode: %s", child)
        if child.todo:
            t = ToDo(child.heading, child.scheduled, path, state=child.todo)
            todos.append(t)
            log.debug("captured: %s", t)
        walknode(child, path)

def visit(root, files):
    log.debug("visit: found files: %s", files)
    for f in files:
        if f.endswith(".org"):
            #if f == "tasks.org":
            #    import pdb; pdb.set_trace()
            path = os.path.join(root, f)
            with open(path, "r") as orgfile:
                log.debug("visit: opening %s", path)
                orgbuf = orgparse.loads(orgfile.read())
                for node in orgbuf[1:]:
                    log.debug("visit: HEADING: %s", node.heading)
                    walknode(node, path)
                    

def walk(rootdir):
    for root, dirs, files in os.walk(rootdir):
        visit(root, files)

def main():
    if len(sys.argv) > 1:
        rootdir = sys.argv[1]
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

    for todo in todos:
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

if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        log.exception("ERROR: uncaught exception: %s", err)
        sys.exit(1)
