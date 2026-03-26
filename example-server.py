#!/usr/bin/env python3

print("Loading model...", flush=True)
import en_core_web_lg as model
# import en_core_sci_scibert as model

# Defaults for en_core_web_md = [tok2vec tagger parser senter attribute_ruler lemmatizer ner sentencizer]
# Reminder: disabling 'parser' seems to cause seg faults :/
nlp = model.load()

# TODO:
# Use nlp.pipe_names to prompt user about which components to enable/disable?

# nlp.max_length = 1500000


from spacy_service.server import serve

port = 50051
max_workers = 10

print("Starting service on port", port, flush=True)
serve(nlp=nlp, port=port, max_workers=max_workers)
