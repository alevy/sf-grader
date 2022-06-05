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

def app_handle(args, context, syscall):
    os.system("ifconfig lo up")
    # Fetch and untar submission tarball
    assignment = context["metadata"]["assignment"]
    with tempfile.NamedTemporaryFile(suffix=".tar.gz") as submission_tar:
        submission_tar_data = syscall.fsread(args['submission'])
        submission_tar.write(submission_tar_data)
        submission_tar.flush()
        with tempfile.TemporaryDirectory() as submission_dir:
            os.system("tar -C %s -xzf %s --strip-components=1" % (submission_dir, submission_tar.name))

            # Fetch and untar grading script tarball
            with tempfile.NamedTemporaryFile(suffix=".tar.gz") as script_tar:
                script_tar_data = syscall.fsread('/cos316/%s/grading_script' % assignment)
                script_tar.write(script_tar_data)
                script_tar.flush()
                with tempfile.TemporaryDirectory() as script_dir:
                    os.system("tar -C %s -xzf %s" % (script_dir, script_tar.name))

                    # OK, run tests
                    os.putenv("GOCACHE", "%s/.cache" % script_dir)
                    os.putenv("GOROOT", "/srv/usr/lib/go")
                    os.putenv("SOLUTION_DIR", submission_dir)
                    os.putenv("PATH", "%s:%s" % ("/srv/usr/lib/go/bin", os.getenv("PATH")))
                    os.chdir(script_dir)
                    if os.path.exists("pretest") and os.access("pretest", os.X_OK):
                        os.system("./pretest")
                    compiledtest = subprocess.Popen("go test -c -o /tmp/grader", shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    compileout, compileerr = compiledtest.communicate()
                    if compiledtest.returncode != 0:
                        return { "error": { "compile": str(compileerr), "returncode": compiledtest.returncode } }
                    testrun = subprocess.Popen("/tmp/grader -test.v | /srv/usr/lib/go/pkg/tool/linux_amd64/test2json", shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                    final_results = []
                    for test_result in testrun.stdout:
                        tr = json.loads(test_result)
                        if tr["Action"] in ["pass", "fail", "run"]:
                            tr = dict((name.lower(), val) for name, val in tr.items())
                            final_results.append(json.dumps(tr))
#                    key = os.path.join(os.path.splitext(args["submission"])[0], "test_results.jsonl")
                    submission = os.path.basename(os.path.splitext(args['submission'])[0])
                    user = context['user']
                    func = context['function']
                    file = '/go_grader/%s/%s/test_results.jsonl' % (user, submission)
                    syscall.endorse_with([[func]])
                    syscall.declassify_to([[user]])
                    syscall.fscreate_dir('/go_grader/%s' % user, submission, syscall.new_dclabel([[user]], [[func]]))
                    syscall.fscreate_file('/go_grader/%s/%s' % (user, submission), os.path.basename(file), syscall.new_dclabel([[user]], [[func]]))
                    syscall.fswrite(file, bytes('\n'.join(final_results), "utf-8"))
                    testrun.wait()
                    if testrun.returncode >= 0:
                        return { "test_results": file }
                    else:
                        _, errlog = testrun.communicate()
                        return { "error": { "testrun": str(errlog), "returncode": testrun.returncode } }
    return {}
