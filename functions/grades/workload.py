import os
import json

def handle(req, data_handles, syscall):
    args = req["args"]
    workflow = req["workflow"]
    context = req["context"]
    result, data_handles_out = app_handle(args, context, data_handles, syscall)
    if len(workflow) > 0:
        next_function = workflow.pop(0)
        syscall.invoke(next_function, json.dumps({
            "args": result,
            "workflow": workflow,
            "context": context
        }), data_handles_out)
    return result

def read_all(opened_blob):
    buf = bytearray()
    while True:
        data = opened_blob.read()
        if len(data) == 0:
            return buf
        buf.extend(data)
    return buf

def app_handle(args, context, data_handles, syscall):
    with syscall.open_unnamed(data_handles['test_results']) as blob:
        test_lines = [ json.loads(line) for line in read_all(blob).split(b'\n') ]
    test_runs = dict((line['test'], line) for line in test_lines if 'test' in line)

    grader_config = "/cos316/%s/grader_config.json" % context["metadata"]["assignment"]
    config = json.loads(syscall.fs_read(grader_config))

    total_points = sum([ test["points"] for test in config["tests"].values() if "extraCredit" not in test or not test["extraCredit"]])

    tests = []
    for (test_name, conf) in config["tests"].items():
        if test_name in test_runs:
            test = test_runs[test_name].copy()
            test["conf"] = conf
            test["subtests"] = { key:val for key, val in test_runs.items() if key.startswith("%s/" % test_name) }
            tests.append(test)

    points = 0.0
    for test in tests:
        if test["action"] == "pass":
            points += test["conf"]["points"]

    output = {
        "points": points,
        "possible": total_points,
        "grade": points / total_points,
        "tests": tests,
        "push_date": context["push_date"]
    }

    assignment = context['metadata']['assignment']
    with syscall.create_unnamed() as blob:
        handle = blob.finalize(bytes(json.dumps(output), "utf-8"))

    return {"grade": points / total_points}, {"grade_report": handle}
