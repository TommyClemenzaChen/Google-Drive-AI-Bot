# AI Bot Integration Project | Google Drive | Nucleo

## Architecture
![image](https://github.com/user-attachments/assets/87b2da0d-917d-4371-b605-1dac8fc2432b)


## Running my application locally




1. Create credentials to your GCP account using a service account

2. Change the config to the folder id of the google drive folder you want to watch


3. Install dependences
```
pip install -r requirements.txt
```

4. Expose your local host and paste the link into reciever_url + /webhook:
```
ngrok http 8080
```

5. run watcher
```
python watcher.py start
```

6. Run the server
```
uvicorn app.main:app --port 8080
```

7. stop the watcher when done
```
python watcher.py stop
```

