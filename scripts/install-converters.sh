#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export VENV="${VENV:-$ROOT/.venv}"
LOCAL_BIN="$ROOT/.local/bin"
LOCAL_LIB="$ROOT/.local/lib"
WORK_DIR="$ROOT/.cache/converters"
BIOFORMATS_HOME="${BIOFORMATS_HOME:-$ROOT/.local/share/bioformats}"
BIOFORMATS_LIB="$BIOFORMATS_HOME/lib"
INSTALL_BIOFORMATS=1
IMGCNV_HOME="${IMGCNV_HOME:-$ROOT/.local/share/imgcnv}"
IMGCNV_VERSION_FILE="$IMGCNV_HOME/version"
IMGCNV_VERSION="${IMGCNV_VERSION:-3.23.0}"
IMGCNV_DEBIAN_RELEASE="${IMGCNV_DEBIAN_RELEASE:-jammy-viqi-1}"
IMGCNV_DEBIAN_ARCH="${IMGCNV_DEBIAN_ARCH:-amd64}"
IMGCNV_PACKAGE_VERSION="${IMGCNV_VERSION}~${IMGCNV_DEBIAN_RELEASE}"
IMGCNV_DEBIAN_BASE_URL="${IMGCNV_DEBIAN_BASE_URL:-https://packages.viqi.org/debian/pool/main/i/imgcnv}"
IMGCNV_DEB="$WORK_DIR/imgcnv_${IMGCNV_PACKAGE_VERSION}_${IMGCNV_DEBIAN_ARCH}.deb"
LIBIMGCNV_DEB="$WORK_DIR/libimgcnv_${IMGCNV_PACKAGE_VERSION}_${IMGCNV_DEBIAN_ARCH}.deb"
IMGCNV_EXTRACT_DIR="$WORK_DIR/imgcnv-${IMGCNV_PACKAGE_VERSION}"

usage() {
  cat <<'USAGE'
Usage: scripts/install-converters.sh [--skip-bioformats]

Install local converter binaries and wrappers.

Options:
  --skip-bioformats  Do not install Bio-Formats Maven artifacts.
  -h, --help         Show this help.

By default, Bio-Formats is installed for local developer setups.
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --skip-bioformats)
      INSTALL_BIOFORMATS=0
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

mkdir -p "$LOCAL_BIN" "$LOCAL_LIB" "$WORK_DIR" "$IMGCNV_HOME"

find_external_imgcnv() {
  local dir candidate
  local old_ifs="$IFS"
  IFS=:
  for dir in $PATH; do
    IFS="$old_ifs"
    [ -n "$dir" ] || continue
    [ "$(cd "$dir" 2>/dev/null && pwd -P)" = "$(cd "$LOCAL_BIN" && pwd -P)" ] && continue
    candidate="$dir/imgcnv"
    if [ -x "$candidate" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
    IFS=:
  done
  IFS="$old_ifs"
  return 1
}

extract_deb() {
  local deb="$1"
  local dest="$2"
  local tmp
  tmp="$(mktemp -d "$WORK_DIR/deb.XXXXXX")"
  (
    cd "$tmp"
    ar x "$deb"
    tar -xf data.tar.* -C "$dest"
  )
  rm -rf "$tmp"
}

flox_native_runtime() {
  local bash_bin interpreter glibc_lib glibc_so lib arrow path rest
  if [ -z "${FLOX_ENV:-}" ] || [ ! -d "$FLOX_ENV" ]; then
    echo "Missing FLOX_ENV. Run inside 'flox activate' so imgcnv can use Flox native libraries." >&2
    return 1
  fi
  if ! command -v patchelf >/dev/null 2>&1; then
    echo "Missing patchelf. Run inside 'flox activate'." >&2
    return 1
  fi

  bash_bin="$(command -v bash || true)"
  if [ -z "$bash_bin" ]; then
    echo "Missing bash in PATH. Run inside 'flox activate'." >&2
    return 1
  fi
  case "$(cd "$(dirname "$bash_bin")/.." && pwd -P)" in
    "$(cd "$FLOX_ENV" && pwd -P)")
      ;;
    *)
      echo "bash is not coming from the active Flox environment: $bash_bin" >&2
      return 1
      ;;
  esac

  interpreter="$(patchelf --print-interpreter "$bash_bin" 2>/dev/null || true)"
  case "$interpreter" in
    /nix/store/*)
      ;;
    *)
      echo "Could not resolve a Flox/Nix dynamic linker from $bash_bin: ${interpreter:-<empty>}" >&2
      return 1
      ;;
  esac
  if [ ! -e "$interpreter" ]; then
    echo "Resolved dynamic linker does not exist: $interpreter" >&2
    return 1
  fi

  glibc_so=""
  while read -r lib arrow path rest; do
    if [ "$lib" = "libc.so.6" ] && [ "$arrow" = "=>" ] && [ -n "$path" ]; then
      glibc_so="$path"
      break
    fi
  done < <(ldd "$bash_bin")
  if [ -z "$glibc_so" ] || [ ! -e "$glibc_so" ]; then
    echo "Could not resolve Flox glibc library directory from $bash_bin." >&2
    return 1
  fi
  glibc_lib="$(dirname "$glibc_so")"

  printf '%s\n%s\n' "$interpreter" "$glibc_lib"
}

patch_imgcnv_interpreter() {
  local interpreter glibc_lib runtime
  local rpath
  if ! patchelf --print-interpreter "$LOCAL_BIN/imgcnv.real" >/dev/null 2>&1; then
    return 0
  fi

  runtime="$(flox_native_runtime)"
  interpreter="$(printf '%s\n' "$runtime" | sed -n '1p')"
  glibc_lib="$(printf '%s\n' "$runtime" | sed -n '2p')"
  rpath="$LOCAL_LIB:$glibc_lib:$FLOX_ENV/lib"
  patchelf --set-interpreter "$interpreter" "$LOCAL_BIN/imgcnv.real"
  patchelf --set-rpath "$rpath" "$LOCAL_BIN/imgcnv.real"
}

download_imgcnv() {
  case "$(uname -s):$(uname -m)" in
    Linux:x86_64|Linux:amd64)
      ;;
    *)
      echo "No bundled VIQI imgcnv package is available for $(uname -s) $(uname -m)." >&2
      echo "Install imgcnv on PATH, then rerun this script." >&2
      exit 1
      ;;
  esac

  if ! command -v ar >/dev/null 2>&1; then
    echo "Missing ar. Run inside 'flox activate' so Debian packages can be extracted." >&2
    exit 1
  fi

  if [ ! -f "$IMGCNV_DEB" ]; then
    curl -fL "$IMGCNV_DEBIAN_BASE_URL/$(basename "$IMGCNV_DEB")" -o "$IMGCNV_DEB"
  fi
  if [ ! -f "$LIBIMGCNV_DEB" ]; then
    curl -fL "$IMGCNV_DEBIAN_BASE_URL/$(basename "$LIBIMGCNV_DEB")" -o "$LIBIMGCNV_DEB"
  fi

  rm -rf "$IMGCNV_EXTRACT_DIR"
  mkdir -p "$IMGCNV_EXTRACT_DIR"
  extract_deb "$IMGCNV_DEB" "$IMGCNV_EXTRACT_DIR"
  extract_deb "$LIBIMGCNV_DEB" "$IMGCNV_EXTRACT_DIR"

  imgcnv_candidate="$IMGCNV_EXTRACT_DIR/usr/bin/imgcnv"
  if [ ! -f "$imgcnv_candidate" ]; then
    echo "Downloaded imgcnv packages did not contain /usr/bin/imgcnv." >&2
    exit 1
  fi

  install -m 0755 "$imgcnv_candidate" "$LOCAL_BIN/imgcnv.real"
  patch_imgcnv_interpreter

  find "$IMGCNV_EXTRACT_DIR/usr/lib" \( -type f -o -type l \) -name 'libimgcnv.so*' \
    -exec cp -P {} "$LOCAL_LIB"/ \;
}

if [ ! -x "$LOCAL_BIN/imgcnv.real" ] || \
   [ ! -f "$IMGCNV_VERSION_FILE" ] || \
   [ "$(cat "$IMGCNV_VERSION_FILE")" != "$IMGCNV_PACKAGE_VERSION" ]; then
  case "$(uname -s):$(uname -m)" in
    Linux:x86_64|Linux:amd64)
      download_imgcnv
      printf '%s\n' "$IMGCNV_PACKAGE_VERSION" > "$IMGCNV_VERSION_FILE"
      ;;
    *)
      external_imgcnv="$(find_external_imgcnv || true)"
      if [ -n "$external_imgcnv" ]; then
        ln -sf "$external_imgcnv" "$LOCAL_BIN/imgcnv.real"
        printf 'external:%s\n' "$external_imgcnv" > "$IMGCNV_VERSION_FILE"
      else
        download_imgcnv
      fi
      ;;
  esac
fi

if [ -x "$LOCAL_BIN/imgcnv.real" ]; then
  patch_imgcnv_interpreter
fi

if [ ! -e "$LOCAL_LIB/libLerc.so.3" ]; then
  lerc4="$(find -L "$FLOX_ENV" -name libLerc.so.4 2>/dev/null | head -1 || true)"
  if [ -n "$lerc4" ]; then
    ln -sf "$lerc4" "$LOCAL_LIB/libLerc.so.3"
  fi
fi

if [ ! -e "$LOCAL_LIB/libhdf5_serial.so.103" ]; then
  hdf5="$(find -L "$FLOX_ENV" -name libhdf5.so.103 2>/dev/null | head -1 || true)"
  if [ -n "$hdf5" ]; then
    ln -sf "$hdf5" "$LOCAL_LIB/libhdf5_serial.so.103"
  fi
fi

if [ ! -e "$LOCAL_LIB/libhdf5_serial_cpp.so.103" ]; then
  hdf5_cpp="$(find -L "$FLOX_ENV" -name libhdf5_cpp.so.103 2>/dev/null | head -1 || true)"
  if [ -n "$hdf5_cpp" ]; then
    ln -sf "$hdf5_cpp" "$LOCAL_LIB/libhdf5_serial_cpp.so.103"
  fi
fi

if [ "$INSTALL_BIOFORMATS" = "1" ]; then
  scripts/install-bioformats.sh
fi

cat > "$LOCAL_BIN/imgcnv" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
base="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
lib="$(cd "$base/../lib" && pwd)"
library_path="$lib"
if [ -n "${FLOX_ENV:-}" ]; then
  for flox_lib in "$FLOX_ENV/lib" "$FLOX_ENV/x86_64-unknown-linux-gnu/lib"; do
    if [ -d "$flox_lib" ]; then
      library_path="$library_path:$flox_lib"
    fi
  done
fi
if [ -n "${NIX_LD_LIBRARY_PATH:-}" ]; then
  library_path="$library_path:$NIX_LD_LIBRARY_PATH"
fi
if [ -n "${LD_LIBRARY_PATH:-}" ]; then
  library_path="$library_path:$LD_LIBRARY_PATH"
fi
export LD_LIBRARY_PATH="$library_path"
export DYLD_LIBRARY_PATH="$lib${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"
err="$(mktemp)"
trap 'rm -f "$err"' EXIT
set +e
if [ -n "${NIX_LD:-}" ] && [ -x "$NIX_LD" ]; then
  "$NIX_LD" --library-path "$library_path" "$base/imgcnv.real" "$@" 2>"$err"
else
  "$base/imgcnv.real" "$@" 2>"$err"
fi
status=$?
set -e
grep -v "no version information available" "$err" >&2 || true
exit "$status"
SH

cat > "$LOCAL_BIN/showinf" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
lib="${BIOFORMATS_HOME:-$root/.local/share/bioformats}/lib"
logback="${BIOFORMATS_HOME:-$root/.local/share/bioformats}/logback.xml"
if [ -d "$lib" ]; then
  exec java -Dlogback.configurationFile="$logback" -cp "$lib/*" loci.formats.tools.ImageInfo "$@"
fi
echo "Bio-Formats showinf is not installed. Run just setup." >&2
exit 127
SH

cat > "$LOCAL_BIN/bfconvert" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
lib="${BIOFORMATS_HOME:-$root/.local/share/bioformats}/lib"
logback="${BIOFORMATS_HOME:-$root/.local/share/bioformats}/logback.xml"
if [ -d "$lib" ]; then
  exec java -Dlogback.configurationFile="$logback" -cp "$lib/*" loci.formats.tools.ImageConverter "$@"
fi
echo "Bio-Formats bfconvert is not installed. Run just setup." >&2
exit 127
SH

cat > "$LOCAL_BIN/formatlist" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
lib="${BIOFORMATS_HOME:-$root/.local/share/bioformats}/lib"
logback="${BIOFORMATS_HOME:-$root/.local/share/bioformats}/logback.xml"
if [ -d "$lib" ]; then
  exec java -Dlogback.configurationFile="$logback" -cp "$lib/*" loci.formats.tools.PrintFormatTable "$@"
fi
echo "Bio-Formats formatlist is not installed. Run just setup." >&2
exit 127
SH

chmod +x "$LOCAL_BIN/imgcnv" "$LOCAL_BIN/showinf" "$LOCAL_BIN/bfconvert" "$LOCAL_BIN/formatlist"

echo "Converter wrappers are installed in $LOCAL_BIN"
