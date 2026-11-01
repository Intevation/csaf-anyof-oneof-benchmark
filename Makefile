.NOTPARALLEL:
.PHONY: support python rust go kotlin

support: python rust go kotlin

python:
	python3 python/main.py fixtures/support

rust:
	cd rust && cargo run --quiet --locked -- ../fixtures/support

go:
	cd go && go run . ../fixtures/support

kotlin:
	cd kotlin && ./gradlew --quiet build run --args=../fixtures/support

REPS ?= 10
DOC_FLAGS ?=
.PHONY: bench-docs bench
bench-docs:
	python3 bench/prepare_schemas.py
	python3 bench/generate_docs.py $(DOC_FLAGS)

bench:
	mkdir -p bench/results
	python3 python/bench.py bench $(REPS) > bench/results/python.csv
	cd rust && cargo run --quiet --locked --release --bin bench -- ../bench $(REPS) > ../bench/results/rust.csv
	cd go && go run ./bench ../bench $(REPS) > ../bench/results/go.csv
	cd kotlin && ./gradlew --quiet bench --args="../bench $(REPS)" > ../bench/results/kotlin.csv
	python3 cli/bench_sourcemeta.py bench $(REPS) > bench/results/sourcemeta.csv
	python3 bench/summarize.py bench/results

.PHONY: support-sourcemeta validate-sourcemeta bench-sourcemeta
bench-sourcemeta:
	mkdir -p bench/results
	python3 cli/bench_sourcemeta.py bench $(REPS) > bench/results/sourcemeta.csv
	python3 bench/summarize.py bench/results

support-sourcemeta:
	python3 cli/sourcemeta.py jsonschema

validate-sourcemeta:
	jsonschema metaschema bench/schema --resolve bench/metaschemas --http
	@status=0; for keyword in anyOf oneOf; do \
		jsonschema validate bench/schema/csaf.$$keyword.json bench/docs --resolve bench/metaschemas --resolve bench/base/SelectionList_2_0_0.schema.json --http || status=1; \
	done; exit $$status
