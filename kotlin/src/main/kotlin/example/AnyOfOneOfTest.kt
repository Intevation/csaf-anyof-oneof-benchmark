// SPDX-License-Identifier: Apache-2.0
// SPDX-FileCopyrightText: 2026 German Federal Office for Information Security (BSI) <https://www.bsi.bund.de>
// Software-Engineering: 2026 Intevation GmbH <https://intevation.de>

package example

import tools.jackson.databind.JsonNode
import tools.jackson.databind.ObjectMapper
import tools.jackson.databind.json.JsonMapper
import com.github.erosb.jsonsKema.JsonParser
import com.github.erosb.jsonsKema.SchemaLoader
import com.github.erosb.jsonsKema.Validator
import com.networknt.schema.InputFormat
import com.networknt.schema.SchemaRegistry
import java.nio.file.Files
import java.nio.file.Path
import kotlin.system.exitProcess

private fun validateNetworknt(schemaText: String, instanceText: String): Boolean {
    val registry = SchemaRegistry.builder().build()
    val schema = registry.getSchema(schemaText, InputFormat.JSON)
    val errors = schema.validate(instanceText, InputFormat.JSON)
    return errors.isEmpty()
}

private fun validateJsonSkema(schemaText: String, instanceText: String): Boolean {
    val schemaJson = JsonParser(schemaText).parse()
    val schema = SchemaLoader(schemaJson).load()
    val validator = Validator.forSchema(schema)
    val instance = JsonParser(instanceText).parse()
    val error = validator.validate(instance)
    return error == null
}

fun main(args: Array<String>) {
    val fixtures = if (args.isEmpty()) Path.of("../fixtures/support") else Path.of(args[0])
    val mapper: ObjectMapper = JsonMapper()
    val cases: JsonNode = mapper.readTree(Files.readString(fixtures.resolve("cases.json")))
    val libraries = listOf("networknt/json-schema-validator", "erosb/json-sKema")
    var failures = 0
    for (library in libraries) {
        for (keyword in listOf("anyOf", "oneOf")) {
            for (case in cases) {
                val name = case["schema"].asText()
                val schemaText = Files.readString(fixtures.resolve("$name.$keyword.json"))
                val instanceText = mapper.writeValueAsString(case["instance"])
                val expected = case[keyword].asBoolean()
                val actual = try {
                    if (library == "networknt/json-schema-validator") {
                        validateNetworknt(schemaText, instanceText)
                    } else {
                        validateJsonSkema(schemaText, instanceText)
                    }
                } catch (e: Exception) {
                    println("ERROR $library $keyword $name: ${case["name"].asText()} (${e})")
                    failures++
                    continue
                }
                var status = "PASS"
                if (actual != expected) {
                    status = "FAIL"
                    failures++
                }
                val caseName = case["name"].asText()
                println("$status $library $keyword $name: $caseName (expected $expected, got $actual)")
            }
        }
    }
    if (failures > 0) exitProcess(1)
}
