from attrdict import AttrDict

foo = AttrDict({
    'bar': AttrDict({})
    })

def set(data):
    data['huhu'] = 'Hello'
    print(data)

set(foo.bar)

print(foo.bar)

set(foo['bar'])

print(foo.bar)
