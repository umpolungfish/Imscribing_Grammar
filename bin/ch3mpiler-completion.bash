# ch3mpiler bash completion — Imscribing Grammar Retrosynthetic Compiler
_ch3mpiler_completions() {
    local cur prev commands
    commands="--target --retrosynthesis --cas --depth --forward --interactive --fg --list-fgs --list-rxns --show-cas-cache --help"
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Top-level flag completion
    if [[ $COMP_CWORD -eq 1 ]]; then
        COMPREPLY=($(compgen -W "${commands}" -- "${cur}"))
        return 0
    fi

    # Suggest target names for --target and --fg
    case "${prev}" in
        --target|--fg)
            COMPREPLY=($(compgen -W "benzaldehyde ethanol acetone acetic_acid methylamine aniline phenol ether toluene anisole nitrobenzene chlorobenzene bromobenzene aspirin acetaminophen 11-Hydroxy-THC" -- "${cur}"))
            ;;
        --cas)
            COMPREPLY=($(compgen -W "50-78-2 103-90-2 69-72-7 64-19-7 67-64-1 67-56-1 64-17-5 71-43-2 100-52-7 3568-94-3 1972-08-3" -- "${cur}"))
            ;;
        --forward)
            COMPREPLY=($(compgen -W "alcohol aldehyde ketone amine acid ester" -- "${cur}"))
            ;;
        --depth)
            COMPREPLY=($(compgen -W "1 2 3 4 5" -- "${cur}"))
            ;;
    esac
}
complete -F _ch3mpiler_completions ch3mpiler
