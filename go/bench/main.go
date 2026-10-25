// SPDX-License-Identifier: Apache-2.0
// SPDX-FileCopyrightText: 2026 German Federal Office for Information Security (BSI) <https://www.bsi.bund.de>
// Software-Engineering: 2026 Intevation GmbH <https://intevation.de>

package main

import (
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"github.com/dlclark/regexp2"
	"github.com/santhosh-tekuri/jsonschema/v6"
)

// Loads remote $refs (meta.json, CVSS, SSVC, ...) online.
// Adapted from https://pkg.go.dev/github.com/santhosh-tekuri/jsonschema/v6#example-package-FromHTTPS
type httpLoader http.Client

func (l *httpLoader) Load(url string) (any, error) {
	client := (*http.Client)(l)
	response, err := client.Get(url)
	if err != nil {
		return nil, err
	}
	defer response.Body.Close()
	if response.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("%s returned status code %d", url, response.StatusCode)
	}
	return jsonschema.UnmarshalJSON(response.Body)
}

type ecmaRegexp regexp2.Regexp

func (re *ecmaRegexp) MatchString(value string) bool {
	matched, err := (*regexp2.Regexp)(re).MatchString(value)
	return err == nil && matched
}

func (re *ecmaRegexp) String() string {
	return (*regexp2.Regexp)(re).String()
}

func compileECMARegexp(expression string) (jsonschema.Regexp, error) {
	re, err := regexp2.Compile(expression, regexp2.ECMAScript)
	if err != nil {
		return nil, err
	}
	return (*ecmaRegexp)(re), nil
}

func readJSON(path string) any {
	file, err := os.Open(path)
	if err != nil {
		panic(err)
	}
	defer file.Close()
	value, err := jsonschema.UnmarshalJSON(file)
	if err != nil {
		panic(err)
	}
	return value
}

// compileSchema prepares a validator before the timed benchmark runs.
func compileSchema(path string) *jsonschema.Schema {
	compiler := jsonschema.NewCompiler()
	compiler.UseRegexpEngine(compileECMARegexp)
	compiler.UseLoader(jsonschema.SchemeURLLoader{
		"file":  jsonschema.FileLoader{},
		"http":  (*httpLoader)(&http.Client{Timeout: 15 * time.Second}),
		"https": (*httpLoader)(&http.Client{Timeout: 15 * time.Second}),
	})

	schemaDocument := readJSON(path)
	schemaURI := schemaDocument.(map[string]any)["$id"].(string)
	// Use the local file instead of fetching the schema from its own $id.
	if err := compiler.AddResource(schemaURI, schemaDocument); err != nil {
		panic(err)
	}
	schema, err := compiler.Compile(schemaURI)
	if err != nil {
		panic(err)
	}
	return schema
}

func main() {
	benchDir := os.Args[1]
	reps, err := strconv.Atoi(os.Args[2])
	if err != nil {
		panic(err)
	}

	keywords := []string{"anyOf", "oneOf"}
	schemas := map[string]*jsonschema.Schema{}
	for _, keyword := range keywords {
		schemaPath := filepath.Join(benchDir, "schema", "csaf."+keyword+".json")
		schemas[keyword] = compileSchema(schemaPath)
	}

	docPaths, err := filepath.Glob(filepath.Join(benchDir, "docs", "*.json"))
	if err != nil {
		panic(err)
	}
	for _, docPath := range docPaths {
		docName := strings.TrimSuffix(filepath.Base(docPath), ".json")
		for rep := 0; rep <= reps; rep++ { // rep 0 is warm-up
			// Alternate which schema runs first so cache effects do not always favor the same variant.
			order := keywords
			if rep%2 == 1 {
				order = []string{"oneOf", "anyOf"}
			}
			for _, keyword := range order {
				loadStart := time.Now()
				data := readJSON(docPath)
				validateStart := time.Now()
				valid := schemas[keyword].Validate(data) == nil
				validateEnd := time.Now()

				loadMs := float64(validateStart.Sub(loadStart).Microseconds()) / 1000
				validateMs := float64(validateEnd.Sub(validateStart).Microseconds()) / 1000
				fmt.Printf("santhosh-tekuri,%s,%s,%d,%.3f,%.3f,%v\n",
					keyword, docName, rep, loadMs, validateMs, valid)
			}
		}
	}
}
