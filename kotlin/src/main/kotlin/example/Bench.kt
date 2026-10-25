// SPDX-License-Identifier: Apache-2.0
// SPDX-FileCopyrightText: 2026 German Federal Office for Information Security (BSI) <https://www.bsi.bund.de>
// Software-Engineering: 2026 Intevation GmbH <https://intevation.de>

package example

import com.github.erosb.jsonsKema.JsonParser
import com.github.erosb.jsonsKema.SchemaLoader
import com.github.erosb.jsonsKema.Validator
import com.networknt.schema.InputFormat
import com.networknt.schema.SchemaRegistry
import java.nio.file.Files
import java.nio.file.Path
import tools.jackson.databind.json.JsonMapper

fun main(args: Array<String>) {
    val bench = Path.of(args[0])
    val reps = args[1].toInt()
    val mapper = JsonMapper()
    val keywords = listOf("anyOf", "oneOf")
    val schemaTexts = mutableMapOf<String, String>()
    for (keyword in keywords) {
        val schemaPath = bench.resolve("schema/csaf.$keyword.json")
        schemaTexts[keyword] = Files.readString(schemaPath)
    }

    // remote $refs (meta.json, CVSS, SSVC, ...) are fetched online
    val schemaLoader = com.networknt.schema.resource.SchemaLoader.builder().fetchRemoteResources().build()
    val registry = SchemaRegistry.builder().schemaLoader(schemaLoader).build()
    val networknt = schemaTexts.mapValues { registry.getSchema(it.value, InputFormat.JSON) }
    val skema = schemaTexts.mapValues { SchemaLoader(JsonParser(it.value).parse()).load() }

    val docsDir = bench.resolve("docs")
    val docs = mutableListOf<Path>()
    Files.list(docsDir).use { paths ->
        for (path in paths) {
            docs.add(path)
        }
    }
    docs.sort()
    for (doc in docs) {
        val stem = doc.fileName.toString().removeSuffix(".json")
        for (rep in 0..reps) {
            val order = if (rep % 2 == 0) keywords else keywords.reversed()
            for (kw in order) {
                for (lib in listOf("networknt", "json-sKema")) {
                    val valid: Boolean
                    val t0: Long
                    val t1: Long
                    val t2: Long
                    if (lib == "networknt") {
                        t0 = System.nanoTime()
                        val text = Files.readString(doc)
                        val node = mapper.readTree(text)
                        t1 = System.nanoTime()
                        valid = networknt[kw]!!.validate(node).isEmpty()
                        t2 = System.nanoTime()
                    } else {
                        t0 = System.nanoTime()
                        val text = Files.readString(doc)
                        val json = JsonParser(text).parse()
                        t1 = System.nanoTime()
                        valid = Validator.forSchema(skema[kw]!!).validate(json) == null
                        t2 = System.nanoTime()
                    }
                    println("$lib,$kw,$stem,$rep,${"%.3f".format((t1 - t0) / 1e6)},${"%.3f".format((t2 - t1) / 1e6)},$valid")
                }
            }
        }
    }
}
