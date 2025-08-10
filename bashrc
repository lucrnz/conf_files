# lucdev's ~/.bashrc - https://git.lucdev.net/lucdev/conf_files

[[ $- != *i* ]] && return
HISTSIZE=1000
HISTFILE=~/.bash_history
HISTCONTROL=ignoredups:erasedups
shopt -s histappend

# functions
cmd_exists() { command -v "$@" &>/dev/null; }
prepend_path() { test -d "$@" && export PATH="$@:$PATH"; }
fork_muted() { "$@" >/dev/null 2>&1 & }
source_ifexists() { test -s "$@" && source "$@"; }
ensure_dir() { [ ! -d "$@" ] || mkdir -p "$@"; }

# env vars
export DOTNET_CLI_TELEMETRY_OPTOUT=1
cmd_exists chromium && export CHROME_EXECUTABLE=$(which chromium)

# path additions
prepend_path "/snap/bin"
prepend_path "$HOME/.local/bin"
prepend_path "$HOME/.conf_files/scripts"
prepend_path "$HOME/.dotnet/tools"
prepend_path "$HOME/.local/opt/flutter_sdk/bin"
prepend_path "$HOME/.local/opt/dotnet"

# completions
source_ifexists "/usr/share/bash-completion/bash_completion"
source_ifexists "/opt/homebrew/etc/profile.d/bash_completion.sh"

# prompt
if cmd_exists starship; then
    eval "$(starship init bash)"
else
    # \h = host, \W = cwd, \$ = prompt char
    PS1='\[\e[38;5;205m\]\h\[\e[0m\]:\[\e[38;5;105m\]\W\[\e[0m\]\$ '
fi

# random tools
if cmd_exists dpkg; then
    apt_autopurge() {
        sudo apt-get purge $(dpkg -l | awk '/^rc/ {print $2}')
    }
fi

# editor
cmd_exists "nano" && export EDITOR=nano
cmd_exists "vim" && export EDITOR=vim
cmd_exists "nvim" && export EDITOR=nvim

# homebrew
if ! cmd_exists brew; then
    if [ -d "/opt/homebrew" ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [ -d "/home/linuxbrew/.linuxbrew" ]; then
        eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    fi
fi

_brew_provides() {
    local bin
    bin=$(command -v "$1" 2>/dev/null) || return 1
    case "$bin" in
        *"/homebrew/"*|*"/linuxbrew/"*) return 0 ;;
        *) return 1 ;;
    esac
}

# brew completions
if [ -d /home/linuxbrew/.linuxbrew/etc/bash_completion.d ]; then
    for completion_file in /home/linuxbrew/.linuxbrew/etc/bash_completion.d/*; do
        source "$completion_file"
    done
fi

# node
if ! _brew_provides node; then
    # try to use nvm
    if [ -f "$HOME/.nvm/nvm.sh" ]; then
        export NVM_DIR="$HOME/.nvm"
        . "$NVM_DIR/nvm.sh"
        source_ifexists "$NVM_DIR/bash_completion"
    else
        if cmd_exists "node" && cmd_exists "npm"; then
            npm_path=$(command -v npm)
            if [[ "$npm_path" == "/usr/bin/npm" || "$npm_path" == "/usr/sbin/npm" ]]; then
                export NPM_CONFIG_PREFIX="$HOME/.npm/packages"
                ensure_dir "$NPM_CONFIG_PREFIX/bin"
                prepend_path "$NPM_CONFIG_PREFIX/bin"
                export NODE_PATH="$NPM_CONFIG_PREFIX/lib/node_modules${NODE_PATH:+:$NODE_PATH}"
            fi
        fi
    fi
fi

# pnpm
if [ -d "$HOME/.local/opt/pnpm" ]; then
    export PNPM_HOME="$HOME/.local/opt/pnpm"
    case ":$PATH:" in
        *":$PNPM_HOME:"*) ;;
        *) export PATH="$PNPM_HOME:$PATH" ;;
    esac
fi

# bun
if ! _brew_provides bun && [ -d "$HOME/.bun" ]; then
    export BUN_INSTALL="$HOME/.bun"
    prepend_path "$BUN_INSTALL/bin"
    source_ifexists "$HOME/.bun/_bun"
fi

# go
if ! _brew_provides go && [ -d "$HOME/.local/opt/go" ]; then
    export GOROOT="$HOME/.local/opt/go"
    export GOPATH="$HOME/go"
    prepend_path "$GOROOT/bin"
    prepend_path "$GOPATH/bin"
fi

# rust
source_ifexists "$HOME/.cargo/env"

# podman
if cmd_exists podman && cmd_exists docker-compose; then
    export DOCKER_HOST="unix://$XDG_RUNTIME_DIR/podman/podman.sock"
fi

# sdkman
if [ -d "$HOME/.sdkman" ]; then
    export SDKMAN_DIR="$HOME/.sdkman"
    source_ifexists "$SDKMAN_DIR/bin/sdkman-init.sh"
fi

# angular CLI
cmd_exists ng && source <(ng completion script)

# aliases
alias ls='ls -l --color=auto'
alias grep='grep --color=auto'
alias _fm="fork_muted"

# host quirks
source_ifexists "$HOME/.conf_files/host_quirks/$HOSTNAME.sh"
