# Deno version manager
# curl -fsSL https://dvm.deno.dev | sh

if test -d "$HOME/.dvm"; then
	export DVM_DIR="$HOME/.dvm"
	export PATH="$DVM_DIR/bin:$PATH"
fi

