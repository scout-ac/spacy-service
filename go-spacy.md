Reminder to myself about how I got [go-spacy](github.com/am-sokolov/go-spacy) working.

```bash
# Resolves issues about symbol lookups.
sudo apt install libpython3.11

python3.11 -m venv venv
source venv/bin/activate
pip install spacy
# en_core_web_sm:
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl#sha256=1932429db727d4bff3deed6b34cfc05df17794f4a52eeb26cf8928f7c1a0fb85

git clone https://github.com/am-sokolov/go-spacy
cd go-spacy
make clean
make
go generate github.com/am-sokolov/go-spacy

cd ..

export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libpython3.11.so
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:"$(pwd)/go-spacy/lib
export CGO_LDFLAGS="-L"$(pwd)"/go-spacy/lib -lpython3.11"
export CGO_ENABLED=1

go mod init whatever
go get github.com/am-sokolov/go-spacy
go run main.go
```

main.go:

```go
package main

import (
	"fmt"
	"log"

	spacy "github.com/am-sokolov/go-spacy"
)

func main() {
	// Initialize NLP with a Spacy model
	nlp, err := spacy.NewNLP("en_core_web_sm") // /home/austinjp/Desktop/go-spacy-experiment/venv-3.11/lib/python3.11/site-packages/en_core_web_sm/en_core_web_sm-3.8.0")
	if err != nil {
		log.Fatal(err)
	}
	defer nlp.Close()

	for {
		var text string
		fmt.Print("Enter text: ")
		fmt.Scan(&text)

		deps := nlp.GetDependencies(text)
		fmt.Printf("%v\n", deps)

		/**
		// Tokenization
		tokens := nlp.Tokenize(text)
		for _, token := range tokens {
			fmt.Printf("Token: %s, POS: %s, Lemma: %s\n",
			 	token.Text, token.POS, token.Lemma,
			)
		}

		// Named Entity Recognition
		entities := nlp.ExtractEntities(text)
		for _, entity := range entities {
			fmt.Printf("Entity: %s [%s]\n", entity.Text, entity.Label)
		}

		// Sentence Splitting
		sentences := nlp.SplitSentences(text)
		for _, sentence := range sentences {
			fmt.Println("Sentence:", sentence)
		}
		*/
	}
}

```
