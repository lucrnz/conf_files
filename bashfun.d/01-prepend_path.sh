prepend_path() { test -d "$@" && export PATH="$@:$PATH"; }