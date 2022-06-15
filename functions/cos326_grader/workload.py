import json
import tempfile
import os
import subprocess

def handle(req, syscall):
    args = req["args"]
    workflow = req["workflow"]
    context = req["context"]
    result = app_handle(args, context, syscall)
    if len(workflow) > 0:
        next_function = workflow.pop(0)
        syscall.invoke(next_function, json.dumps({
            "args": result,
            "workflow": workflow,
            "context": context
        }))
    return result

def app_handle(args, state, syscall):
    testrun = subprocess.Popen("/srv/usr/bin/ocamlc -v 2>&1", shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    testout, testerr = testrun.communicate()
    return { "test_results": testout.decode('utf-8'), }

