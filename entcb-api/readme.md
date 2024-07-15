curl -X POST http://127.0.0.1:8000/auth/create-client \
     -H "Content-Type: application/json" \
     -H "X-Golden-Key: 7fadhAY7gfa445dsfkadsfu" \
     -d '{"client_name": "New_test"}'

curl -X POST "http://127.0.0.1:8000/s3op/create_chatbot" \
     -H "Content-Type: application/json" \
     -H "Secret-Key: 6d73fd0049cef3deb64f1e2a86b1deadaae454e9b111736aa047206e58a9ec04" \
     -H "Access-Key: 06d2f3a36a96c224ba9610c332a20762e1d196223a0fadfdb3f44d3073475af0" \
     -d '{"custom_id": "New_test", "chat_bot": "Sales"}'
