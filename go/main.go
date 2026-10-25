// SPDX-License-Identifier: Apache-2.0
// SPDX-FileCopyrightText: 2026 German Federal Office for Information Security (BSI) <https://www.bsi.bund.de>
// Software-Engineering: 2026 Intevation GmbH <https://intevation.de>

package main

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/dlclark/regexp2"
	"github.com/santhosh-tekuri/jsonschema/v6"
)

type ecmaRegexp regexp2.Regexp

func (re *ecmaRegexp) MatchString(value string) bool {
	matched, err := (*regexp2.Regexp)(re).MatchString(value)
	return err == nil && matched
}

func (re *ecmaRegexp) String() string { return (*regexp2.Regexp)(re).String() }

func compileECMARegexp(expression string) (jsonschema.Regexp, error) {
	re, err := regexp2.Compile(expression, regexp2.ECMAScript)
	if err != nil {
		return nil, err
	}
	return (*ecmaRegexp)(re), nil
}

func readJSON(path string) (any, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	return jsonschema.UnmarshalJSON(f)
}

func main() {
	fixtures := "../fixtures/support"
	if len(os.Args) > 1 {
		fixtures = os.Args[1]
	}
	casesDoc, err := readJSON(filepath.Join(fixtures, "cases.json"))
	if err != nil {
		panic(err)
	}
	failures := 0
	for _, keyword := range []string{"anyOf", "oneOf"} {
		for _, c := range casesDoc.([]any) {
			cm := c.(map[string]any)
			name := cm["schema"].(string)
			doc, err := readJSON(filepath.Join(fixtures, name+"."+keyword+".json"))
			if err != nil {
				panic(err)
			}
			compiler := jsonschema.NewCompiler()
			compiler.UseRegexpEngine(compileECMARegexp)
			uri := "https://example.com/" + name + "." + keyword + ".json"
			if err := compiler.AddResource(uri, doc); err != nil {
				panic(err)
			}
			schema, err := compiler.Compile(uri)
			if err != nil {
				panic(err)
			}
			actual := schema.Validate(cm["instance"]) == nil
			expected := cm[keyword].(bool)
			status := "PASS"
			if actual != expected {
				status = "FAIL"
				failures++
			}
			fmt.Printf("%s santhosh-tekuri/jsonschema %s %s: %s (expected %v, got %v)\n", status, keyword, name, cm["name"], expected, actual)
		}
	}
	if failures > 0 {
		os.Exit(1)
	}
}
