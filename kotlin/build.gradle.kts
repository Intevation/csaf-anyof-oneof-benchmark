import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    kotlin("jvm") version "2.4.10"
    application
}

group = "example.com"
version = "0.1.0"

repositories {
    mavenCentral()
}

dependencies {
    implementation("com.github.erosb:json-sKema:0.28.0")
    implementation("com.networknt:json-schema-validator:3.0.6")
    implementation("tools.jackson.core:jackson-databind:3.1.4")
    runtimeOnly("org.slf4j:slf4j-simple:2.0.17")
}

java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

kotlin {
    compilerOptions {
        jvmTarget = JvmTarget.JVM_17
    }
}

application {
    mainClass = "example.AnyOfOneOfTestKt"
    applicationDefaultJvmArgs = listOf("-Dorg.slf4j.simpleLogger.defaultLogLevel=error")
}

tasks.register<JavaExec>("bench") {
    classpath = sourceSets["main"].runtimeClasspath
    mainClass = "example.BenchKt"
    jvmArgs("-Xmx4g", "-Dorg.slf4j.simpleLogger.defaultLogLevel=error")
}
