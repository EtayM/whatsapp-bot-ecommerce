### 1st terminal:
Generate tunnel with ngrok, for the callback url
```
ngrok http 5000
```
Then insert the URL on meta cloud. (https://developers.facebook.com)

### 2nd terminal:
Run celery:
```
celery -A tasks worker --pool=solo --loglevel=info
```

### 3rd terminal:
to activate the venv run
```
.\waaffiliate\Scripts\activate
```
Then run the app with
```
python app.py
```