import json
import random

adjectives ="""autumn hidden bitter misty silent empty dry dark summer
icy delicate quiet white cool spring winter patient
twilight dawn crimson wispy weathered blue billowing
broken cold damp falling frosty green long late lingering
bold little morning muddy old red rough still small
sparkling thrumming shy wandering withered wild black
young holy solitary fragrant aged snowy proud floral
restless divine polished ancient purple lively nameless""".split()

nouns = """waterfall river breeze moon rain wind sea morning
snow lake sunset pine shadow leaf dawn glitter forest
hill cloud meadow sun glade bird brook butterfly
bush dew dust field fire flower firefly feather grass
haze mountain night pond darkness snowflake silence
sound sky shape surf thunder violet water wildflower
wave water resonance sun log dream cherry tree fog
frost voice paper frog smoke star""".split()

def handle(req, syscall):
    assignments = json.loads(syscall.read_key(b'cos316/assignments'))
    if req["assignment"] not in assignments:
        return { 'error': 'No such assignment' }

    users = set(req['users'])
    group_size = (assignment["assignment"]["group_size"] or 1)
    if len(users) != group_size:
        return { 'error': 'This assignment requires a group size of %d, given %d.' % (group_size, len(users)) }

    for user in users:
        repo = syscall.read_key(bytes('cos316/assignments/%s/%s' % (req["assignment"], user), 'utf-8'));
        if repo:
            return {
                'error': ("%s is already completing %s at %s" % (user, req['assignment'], repo.decode('utf-8')))
            }

    resp = None
    name = None
    for i in range(0, 3):
        name = '-'.join([req["assignment"], random.choice(adjectives), random.choice(nouns)])
        api_route = "/repos/%s/generate" % (assignments[req["assignment"]]["starter_code"])
        body = {
                'owner': 'cos316',
                'name': name,
                'private': True
        }
        resp = syscall.github_rest_post(api_route, body);
        if resp.status == 201:
                break
        elif i == 2:
            return { 'error': "Can't find a unique repository name", "status": resp.status }

    for user in req['gh_handles']:
        api_route = "/repos/cos316/%s/collaborators/%s" % (name, user)
        body = {
            'permission': 'push'
        }
        resp = syscall.github_rest_put(api_route, body);
        if resp.status > 204:
            return { 'error': "Couldn't add user to repository", "status": resp.status }


    syscall.write_key(bytes('github/cos316/%s/_meta' % name, 'utf-8'),
                      bytes(json.dumps({
                          'assignment': req['assignment'],
                          'users': list(users),
                      }), 'utf-8'))
    syscall.write_key(bytes('github/cos316/%s/_workflow' % name, 'utf-8'),
                      bytes(json.dumps(["go_grader", "grades", "generate_report", "post_comment"]), 'utf-8'))
    for user in users:
        syscall.write_key(bytes('cos316/assignments/%s/%s' % (req["assignment"], user), 'utf-8'),
                          bytes("cos316/%s" % name, 'utf-8'))

    return { 'name': name, 'users': list(users), 'github_handles': req['gh_handles'] }
