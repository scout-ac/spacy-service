#!/usr/bin/env python3


print("Loading models...", flush=True)
import en_core_web_lg as model
import coreferee


# Defaults for en_core_web_md = [tok2vec tagger parser senter attribute_ruler lemmatizer ner sentencizer]
# Reminder: disabling 'parser' seems to cause seg faults :/
# TODO:
# Use nlp.pipe_names to prompt user about which components to enable/disable?

nlp = model.load()
nlp.add_pipe("coreferee")


from spacy_service.server import serve

port = 50051
max_workers = 10

print("Starting service on port", port, flush=True)
serve(nlp=nlp, port=port, max_workers=max_workers)
