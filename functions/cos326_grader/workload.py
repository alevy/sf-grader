import json
import tempfile
import os
import subprocess
import shutil

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
    assignment = state["metadata"]["assignment"]

    with tempfile.TemporaryDirectory() as workdir:
        shutil.copy("/srv/utils326.ml", workdir)
        os.chdir(workdir)
        os.putenv("OCAMLLIB", "/srv/usr/lib/ocaml")

        with tempfile.NamedTemporaryFile(suffix=".tar.gz") as submission_tar:
            submission_tar_data = syscall.read_key(bytes(args["submission"], "utf-8"))
            submission_tar.write(submission_tar_data)
            submission_tar.flush()
            os.mkdir("submission")
            os.system("tar -C submission -xzf %s --strip-components=1" % submission_tar.name)
            os.putenv("SUBMISSION_DIR", "submission")
            with tempfile.NamedTemporaryFile(suffix=".tar.gz") as script_tar:
                script_tar_data = syscall.read_key(bytes("cos326/%s/grading_script" % assignment, "utf-8"))
                script_tar.write(script_tar_data)
                script_tar.flush()
                os.system("tar -C submission -xzf %s" % script_tar.name)

                compilerun = subprocess.Popen(f"PATH=/srv/usr/bin:{os.environ['PATH']} make -sef submission/Makefile", shell=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                compileout, compileerr = compilerun.communicate()

                if compilerun.returncode != 0:
                    return { "error": { "compile": compileerr.decode("utf-8"), "returncode": compilerun.returncode } }

        testrun = subprocess.Popen("/srv/usr/bin/ocamlrun a.out 2>&1", shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        testout, testerr = testrun.communicate()

        report_key = args['submission'] + "/report"
        syscall.write_key(report_key.encode('utf-8'), testout)
        return { "report": report_key, "test_stderr": testerr.decode('utf-8') }

