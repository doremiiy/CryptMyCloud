# Server Api Guide

## Get auth token
```
auth_token = requests.post(
    'http://localhost:8000/api-token-auth/',
    json={'username': 'remid', 'password': 'password'}
).json()[token]
```

## Refresh auth token
```
requests.post('http:/localhost:8000/api-token-refresh/', json={'token': auth_token})
```

## Creation of a file
```
result = requests.post('http://localhost:8000/file/', data={'file_name': 'test.txt'})
```

## Delete a file
```
requests.delete(
    'http://localhost:8000/file/',
    params={'file_name': 'test.txt'}, headers={'Authorization': 'JWT %s' % auth_token }
)
```

## Retrieve key
```
result = requests.get(
    'http://localhost:8000/file/',
    params={'file_name': 'test.txt'},
    headers={'Authorization': 'JWT %s' % auth_token }
)
```

## List of files
```
requests.get('http://localhost:8000/file/list/', headers={'Authorization': 'JWT %s' % auth_token})
```
