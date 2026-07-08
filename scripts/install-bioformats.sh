#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BIOFORMATS_VERSION="${BIOFORMATS_VERSION:-8.3.0}"
BIOFORMATS_HOME="${BIOFORMATS_HOME:-$ROOT/.local/share/bioformats}"
BIOFORMATS_LIB="$BIOFORMATS_HOME/lib"
BIOFORMATS_VERSION_FILE="$BIOFORMATS_HOME/version"
BIOFORMATS_LOGBACK="$BIOFORMATS_HOME/logback.xml"
MAVEN_REPO="${MAVEN_REPO:-$ROOT/.cache/maven}"
WORK_DIR="$ROOT/.cache/bioformats"
POM="$WORK_DIR/pom.xml"

if ! command -v mvn >/dev/null 2>&1; then
  echo "Missing mvn. Run inside 'flox activate' after the Flox environment updates." >&2
  exit 1
fi

if [ -f "$BIOFORMATS_VERSION_FILE" ] && \
   [ "$(cat "$BIOFORMATS_VERSION_FILE")" = "$BIOFORMATS_VERSION" ] && \
   find "$BIOFORMATS_LIB" -name 'bio-formats-tools-*.jar' -print -quit | grep -q . && \
   find "$BIOFORMATS_LIB" -name 'logback-classic-*.jar' -print -quit | grep -q .; then
  exit 0
fi

mkdir -p "$WORK_DIR" "$BIOFORMATS_HOME"

cat > "$POM" <<EOF
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>bisque.dev</groupId>
  <artifactId>bioformats-runtime</artifactId>
  <version>1</version>
  <repositories>
    <repository>
      <id>ome-releases</id>
      <url>https://artifacts.openmicroscopy.org/artifactory/ome.releases/</url>
    </repository>
    <repository>
      <id>scijava-public</id>
      <url>https://maven.scijava.org/content/repositories/public/</url>
    </repository>
  </repositories>
  <dependencies>
    <dependency>
      <groupId>ome</groupId>
      <artifactId>bioformats_package</artifactId>
      <version>${BIOFORMATS_VERSION}</version>
      <type>pom</type>
    </dependency>
    <dependency>
      <groupId>ch.qos.logback</groupId>
      <artifactId>logback-classic</artifactId>
      <version>1.3.15</version>
    </dependency>
  </dependencies>
</project>
EOF

tmp_lib="$(mktemp -d "$WORK_DIR/lib.XXXXXX")"
trap 'rm -rf "$tmp_lib"' EXIT

mvn -q \
  -f "$POM" \
  -Dmaven.repo.local="$MAVEN_REPO" \
  org.apache.maven.plugins:maven-dependency-plugin:3.6.1:copy-dependencies \
  -DincludeScope=runtime \
  -DoutputDirectory="$tmp_lib"

if ! find "$tmp_lib" -name 'bio-formats-tools-*.jar' -print -quit | grep -q .; then
  echo "Bio-Formats Maven install did not produce bio-formats-tools for $BIOFORMATS_VERSION." >&2
  exit 1
fi

rm -rf "$BIOFORMATS_LIB"
mv "$tmp_lib" "$BIOFORMATS_LIB"
trap - EXIT
cat > "$BIOFORMATS_LOGBACK" <<'EOF'
<configuration>
  <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
    <target>System.out</target>
    <encoder>
      <pattern>%msg%n</pattern>
    </encoder>
  </appender>
  <root level="INFO">
    <appender-ref ref="STDOUT" />
  </root>
</configuration>
EOF
printf '%s\n' "$BIOFORMATS_VERSION" > "$BIOFORMATS_VERSION_FILE"

echo "Bio-Formats $BIOFORMATS_VERSION Maven dependencies installed in $BIOFORMATS_LIB"
