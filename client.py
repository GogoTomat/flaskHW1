import requests
import datetime

HOST = 'http://127.0.0.1:5000'


data = requests.post(f'{HOST}/login/', json={
    'username': 'admin3',
    'password': '123456789'
})


print(data.json())
