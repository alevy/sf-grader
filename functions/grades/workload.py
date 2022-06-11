import os
import json

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
    test_lines = [ json.loads(line) for line in syscall.fs_read(args['test_results']).split(b'\n') ]
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
    file = 'grade.json'
    syscall.workspace_createdir(assignment)
    syscall.workspace_createfile(file, assignment)
    syscall.workspace_write(os.path.join(assignment, file), bytes(json.dumps(output), "utf-8"))

    return {
        "grade": points / total_points,
        "grade_report": syscall.workspace_abspath(os.path.join(assignment, file))
    }
