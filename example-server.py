#!/usr/bin/env python3

host = "localhost"
port = 50051
max_workers = 10


# Check port is available:
import socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    if sock.connect_ex((host, port)) == 0:
        print(f"Port {port} already in use! Quitting!")
        exit(1)


# Load spaCy model.
print("Loading spacy...", flush=True)
import en_core_web_lg as model
nlp = model.load()


# Add coreferencing.
print("Loading coreferee...", flush=True)
import coreferee
nlp.add_pipe("coreferee")


# Start the server.
from spacy_service.server import serve
print("Starting service on port", port, flush=True)
serve(nlp=nlp, port=port, max_workers=max_workers)
