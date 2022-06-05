import json
import tempfile
import os
import time

def handle(req, syscall):
#    key = "github/%s/%s.tgz" % (req["repository"]["full_name"], req["after"])
#    meta_key = "github/%s/_meta" % (req["repository"]["full_name"])
#    workflow_key = "github/%s/_workflow" % (req["repository"]["full_name"])
    usergroup = req['repository']['full_name']
    key = '/gh_repo/%s/%s.tgz' % (req['repository']['full_name'], req['after'])
    base_dir = '/gh_repo/%s' % usergroup
    meta_path = '/start_assignment/%s/_meta' % usergroup
    workflow_path = '/start_assignment/%s/_workflow' % usergroup

    metadataString = syscall.fsread(meta_path) or "{}"
    if metadataString:
        metadata = json.loads(metadataString)
        workflow = json.loads(syscall.fsread(workflow_path) or "[]")

        resp = syscall.github_rest_get("/repos/%s/tarball/%s" % (req["repository"]["full_name"], req["after"]));
        syscall.fscreate_file(base_dir, '%s.tgz' % req['after'], syscall.get_current_label())
        syscall.fswrite(path, resp.data)

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
