_ch3mpiler_ob3ect_completions() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    opts="--help --quiet"
    COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") )
    return 0
}
complete -F _ch3mpiler_ob3ect_completions ch3mpiler-ob3ect
