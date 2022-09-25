import requests

# x = requests.get('http://localhost:5000/test_insert')
# x = requests.get('http://localhost:5000/test_insertpet')
# x = requests.get('http://localhost:5000/test_insertexam')
# print(x.status_code)

requests.post('http://localhost:5000/insert_user', data={'first_name': 'Dimitris', 'last_name': 'Charitos', 'email':'dimitris@gmail', 'role':'admin'})