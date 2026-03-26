from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from grpc import server as grpc_server
from grpc._server import _Context as grpc_server_context
from grpclib.server import Server
from spacy.language import Language
from spacy.tokens import Doc as SpacyDoc, Span as SpacySpan
from spacy_service.generated import spacy_service_pb2_grpc
from spacy_service.generated.spacy_service_pb2 import (
    Ancestors, Children, Conjuncts, Doc, Ent, GetDocRequest,
    Lefts, Rights, Sent, Span, Subtree, Token
)


class SpacyService(spacy_service_pb2_grpc.SpacyServiceServicer):
    def __init__(self, nlp:Language) -> None:
        self.nlp = nlp

    def _ents(self, doc:SpacyDoc|SpacySpan, request:GetDocRequest) -> list[Ent]:
        return [
            Ent(
                start=ent.start,
                start_char=ent.start_char,
                end=ent.end,
                end_char=ent.end_char,
                label=ent.label_,
                sentiment=None if request.skip_sentiment else ent.sentiment,
            )
            for ent in doc.ents
        ]

    def _sents(self, doc:SpacyDoc, request:GetDocRequest) -> list[Sent]:
        return [
            Sent(
                start=sent.start,
                start_char=sent.start_char,
                end=sent.end,
                end_char=sent.end_char,
                label=sent.label_,
                sentiment=sent.sentiment,
                ents=None if request.skip_ents else self._ents(sent, request),
            )
            for sent in doc.sents
        ]

    def _tokenize(self, doc:SpacyDoc, request:GetDocRequest) -> list[Token]:
        # Pre-size list for a bit of efficiency.
        tokens = [None] * len(doc)

        text = doc.text
        len_text = len(text)

        print("Processing tokens...")
        start = datetime.now()
        for idx, tok in enumerate(doc):
            ancestors, children, conjuncts, lefts, rights, subtree = [None] * 6
            if request.ancestors:
                ancestors = Ancestors(i=[_.i for _ in tok.ancestors ])
            if request.children:
                children = Children(i=[_.i for _ in tok.children ])
            if request.conjuncts:
                conjuncts = Conjuncts(i=[_.i for _ in tok.conjuncts ])
            if request.lefts:
                lefts = Lefts(i=[_.i for _ in tok.lefts ])
            if request.rights:
                rights = Rights(i=[_.i for _ in tok.rights ])
            if request.subtree:
                subtree = Subtree(i=[_.i for _ in tok.subtree ])

            tokens[idx] = Token(
                i=tok.i,
                start_char=tok.idx,
                end_char=min(tok.idx+len(tok), len_text),
                tag=tok.tag_,
                morph=str(tok.morph),
                lemma=tok.lemma_,
                dep=tok.dep_,
                ent_type=tok.ent_type_,
                head=tok.head.i,
                is_alpha=tok.is_alpha,
                is_ascii=tok.is_ascii,
                is_bracket=tok.is_bracket,
                is_currency=tok.is_currency,
                is_digit=tok.is_digit,
                is_left_punct=tok.is_left_punct,
                is_lower=tok.is_lower,
                is_punct=tok.is_punct,
                is_quote=tok.is_quote,
                is_right_punct=tok.is_right_punct,
                is_sent_end=tok.is_sent_end,
                is_sent_start=tok.is_sent_start,
                is_space=tok.is_space,
                is_stop=tok.is_stop,
                is_title=tok.is_title,
                is_upper=tok.is_upper,
                like_email=tok.like_email,
                like_num=tok.like_num,
                like_url=tok.like_url,
                lang=tok.lang_,
                lower=tok.lower_,
                sentiment=tok.sentiment,
                ancestors=ancestors,
                children=children,
                lefts=lefts,
                rights=rights,
                conjuncts=conjuncts,
                subtree=subtree,
                text=tok.text,
            )
        end = datetime.now()
        print("Tokens processed, it took: " + str(end-start))
        return tokens

    def GetDoc(self, request:GetDocRequest, context:grpc_server_context) -> Doc:
        print("Got " + str(len(request.text)) + " characters.")
        # Spacy models' NER and parser use 1GB RAM per 100,000 characters,
        # so can fail with text > nlp.max_length characters.
        # Truncate to 95% of nlp.max_length:
        trunc_len = self.nlp.max_length - int(self.nlp.max_length * 0.05)
        truncated = request.text[:trunc_len]
        if len(truncated) < len(request.text):
            print("Truncated to " + str(len(truncated)) + " characters.")

        print("Processing doc...")
        start = datetime.now()
        doc = self.nlp(truncated)
        end = datetime.now()
        print("Doc processed, it took: " + str(end-start))

        text = doc.text
        len_text = len(text)
        print("Text length (chars):  " + str(len_text))
        print("Text length (tokens): " + str(len(doc)))

        sents: list[Sent] = []
        if not request.skip_sents:
            start = datetime.now()
            sents = self._sents(doc, request)
            end = datetime.now()
            print("Made sents, took " + str(end-start))

        ents: list[Ent] = []
        if not request.skip_ents:
            start = datetime.now()
            ents = self._ents(doc, request)
            end = datetime.now()
            print("Made ents, took  " + str(end-start))

        # spans = [
        #     Spans(
        #         start=span.start,
        #         start_char=span.start_char,
        #         end=span.end,
        #         end_char=span.end_char,
        #         sentiment=span.sentiment,
        #     )
        #     for span in doc.spans
        # ]

        ######################################################################

        tokens: list[Token] = []
        if request.tokenize:
            tokens = self._tokenize(doc, request)

        sentiment: float = 0.0
        if not request.skip_sentiment:
            sentiment = doc.sentiment

        ret = Doc(
            text=text if text else None,
            ents=ents if ents else None,
            sents=sents if sents else None,
            sentiment=sentiment if sentiment != 0.0 else None,
            tokens=tokens if tokens else None,
        )
        print("Done!")
        return ret


def serve(
        nlp:Language,
        port:int=50051,
        max_workers:int=10,
) -> None:
    server = grpc_server(
        ThreadPoolExecutor(max_workers=max_workers),
        options=[
            ("grpc.max_send_message_length", -1),
            ("grpc.max_receive_message_length", -1),
        ]
    )
    spacy_service_pb2_grpc.add_SpacyServiceServicer_to_server(SpacyService(nlp=nlp), server)
    server.add_insecure_port(f'[::]:{port}')
    print(f'Server starting with {max_workers} workers (max) on port {port}...')
    server.start()
    print("Ready!")
    server.wait_for_termination()
