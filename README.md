# spacy-service

Run spaCy as a GRPC service.

## What

[SpaCy](https://spacy.io/) is a hugely popular and powerful tool for natural language processing.
The team at [Explosion](https://explosion.ai) provide several excellent models so spaCy can run out-of-the-box with minimal fuss.

`spacy-service` simply runs a spaCy model behind a [GRPC](https://grpc.io/) server, thereby making it accessible to GRPC clients.


## Why

SpaCy is predominantly for the Python ecosystem.
If you need spaCy's capabilities but you work in other languages, you have little option other than to run spaCy as a 'sidecar' process.
You then need to figure out how to communicate with spaCy.
That's where this project comes in: we've done that work for you.


### Why GRPC?

It's fast, efficient, and widely available.
It's also lean over the wire, which we feel makes it superior to JSON.

Don't worry, if you really want JSON you can still use [the client](https://scout.ac/go/spacy-service-client) which enables simple serialization to JSON.


## How

Install and start the service:

```bash
git clone https://github.com/scout-ac/spacy-service
cd spacy-service
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python ./example-server.py
```

See [`example-server.py`](https://github.com/scout-ac/spacy-service/blob/main/example-server.py) for a basic server configuration.
Authentication and more sophisticated arrangements are left as an exercise for you :smile:

You can then connect a GRPC client to `localhost:50051` or wherever you choose to host the service.
The response can be serialized to JSON, see the [client](https://scout.ac/go/spacy-service-client) library for details.


## Prior art

- [ceh137/spacy_go_client](https://github.com/ceh137/spacy_go_client) is a client for [jgontrum/spacy-api-docker](https://github.com/jgontrum/spacy-api-docker).
- [am-sokolov/go-spacy](https://github.com/am-sokolov/go-spacy) provides Golang bindings for SpaCy through an optimized C++ bridge layer, but I couldn't get it working.


## Contributing

See [CONTRIBUTING.md](https://github.com/scout-ac/spacy-service/blob/main/CONTRIBUTING.md)
