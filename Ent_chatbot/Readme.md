.
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── auth.py
│   ├── s3_utils.py
│   ├── endpoints
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── chatbot.py
│   │   ├── backup.py
│   │   ├── upload.py
│   │   ├── restore.py
├── .env
├── requirements.txt


curl -X POST "http://localhost:8000/client/create_client" -H "Content-Type: application/json" -d '{
  "client_id": "New_chatbot",
  "golden_key": "123456789"
}'
