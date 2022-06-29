import json
import tempfile
import os
import time

def handle(req, syscall):
    key = "github/%s/%s.tgz" % (req["repository"]["full_name"], req["after"])
    meta_key = "github/%s/_meta" % (req["repository"]["full_name"])
    workflow_key = "github/%s/_workflow" % (req["repository"]["full_name"])

    metadataString = syscall.read_key(bytes(meta_key, "utf-8")) or "{}"
    if metadataString:
        metadata = json.loads(metadataString)
        workflow = json.loads(syscall.read_key(bytes(workflow_key, "utf-8")) or "[]")

        resp = syscall.github_rest_get("/repos/%s/tarball/%s" % (req["repository"]["full_name"], req["after"]));
        syscall.write_key(bytes(key, "utf-8"), resp.data)

        if len(workflow) > 0:
            next_function = workflow.pop(0)
            syscall.invoke(next_function, json.dumps({
                "args": {
                    "submission": key
                },
                "workflow": workflow,
                "context": {
                    "repository": req["repository"]["full_name"],
                    "commit": req["after"],
                    "push_date": req["repository"]["pushed_at"],
                    "metadata": metadata
                }
            }))
        return { "written": len(resp.data), "key": key }
    else:
        return {}
