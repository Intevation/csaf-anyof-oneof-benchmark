.NOTPARALLEL:
.PHONY: support python rust go kotlin

support: python rust go kotlin

python:
	cd python && uv run --quiet main.py ../fixtures/support

rust:
	cd rust && cargo run --quiet --locked -- ../fixtures/support

go:
	cd go && go run . ../fixtures/support

kotlin:
	cd kotlin && ./gradlew --quiet build run --args=../fixtures/support

REPS ?= 10
.PHONY: bench-docs bench
bench-docs:
	cd bench && python3 prepare_schemas.py && python3 generate_docs.py

bench:
	mkdir -p bench/results
	cd python && uv run --quiet bench.py ../bench $(REPS) > ../bench/results/python.csv
	cd rust && cargo run --quiet --locked --release --bin bench -- ../bench $(REPS) > ../bench/results/rust.csv
	cd go && go run ./bench ../bench $(REPS) > ../bench/results/go.csv
	cd kotlin && ./gradlew --quiet bench --args="../bench $(REPS)" > ../bench/results/kotlin.csv
	python3 bench/summarize.py bench/results
