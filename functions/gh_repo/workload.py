import json
import tempfile
import os
import time

def handle(req, syscall):
    repo_full_name = req["repository"]["full_name"]
    meta_path = "/github/%s/_meta" % (req_full_name)
    workflow_path = "/github/%s/_workflow" % (req_full_name)

    # if success, the function's secrecy is raised to the _meta file's secrecy
    # otherwise, the function's secrecy is raised to the /github/OWNER/REPO directory's secrecy
    # the former secrecy is as high as the latter secrecy at least
    metadata = json.loads(syscall.fs_read(meta_path) or "{}")
    workflow = json.loads(syscall.fs_read(workflow_path) or "[]")

    gh_repo = '/github/%s/gh_repo' % req_full_name
    tarball_path = '%s/%s.tgz' % (github_repo, req['after'])
    # try to create the /github/OWNER/REPO directory
    # if the directory doesn't already exist, this implies _meta and _workflow don't exist
    # and, therefore, the directory will be created with the label <OWNER, gh_repo>
    syscall.fs_createdir(github_repo)
    resp = syscall.github_rest_get("/repos/%s/tarball/%s" % (req_full_name, req["after"]));
    syscall.fs_createfile(tarball_path)
    syscall.fs_write(tarball_path, resp.data)

    if len(workflow) > 0:
        next_function = workflow.pop(0)
        payload = json.dumps({
            "args": {
                "submission": path
            },
            "workflow": workflow,
            "context": {
                "repository": req["repository"]["full_name"],
                "commit": req["after"],
                "push_date": req["repository"]["pushed_at"],
                "metadata": metadata
            }
        })
        data_handles = {}
        syscall.invoke(next_function, payload, data_handles)
    return { "written": len(resp.data), "path": path }
