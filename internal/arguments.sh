#!/usr/bin/env bash

source $(which log.sh)

OPTIONAL_ARGUMENTS_NAMES=()
OPTIONAL_ARGUMENTS_STORE_VARIABLES=()
OPTIONAL_ARGUMENTS_DEFAULT_VALUES=()
OPTIONAL_ARGUMENTS_HELP_MESSAGES=()

POSITIONAL_ARGUMENTS_STORE_VARIABLES=()
POSITIONAL_ARGUMENTS_HELP_MESSAGES=()

register_optional_argument() {
    name=${1}
    store_variable=${2}
    default_value=${3}
    help_message=${4}

    OPTIONAL_ARGUMENTS_NAMES+=("${name}")
    OPTIONAL_ARGUMENTS_STORE_VARIABLES+=("${store_variable}")
    OPTIONAL_ARGUMENTS_DEFAULT_VALUES+=("${default_value}")
    OPTIONAL_ARGUMENTS_HELP_MESSAGES+=("${help_message}")
}

register_positional_argument() {
    store_variable=${1}
    help_message=${2}

    POSITIONAL_ARGUMENTS_STORE_VARIABLES+=("${store_variable}")
    POSITIONAL_ARGUMENTS_HELP_MESSAGES+=("${help_message}")
}

print_arguments_help_message() {
    echo "Optional arguments:"
    for i in ${!OPTIONAL_ARGUMENTS_STORE_VARIABLES[*]}; do
        echo -e "\t${OPTIONAL_ARGUMENTS_NAMES[${i}]}\t\t${OPTIONAL_ARGUMENTS_HELP_MESSAGES[${i}]} (default: ${OPTIONAL_ARGUMENTS_DEFAULT_VALUES[${i}]})"
    done
    echo "Positional arguments:"
    for i in ${!POSITIONAL_ARGUMENTS_STORE_VARIABLES[*]}; do
        echo -e "\t${POSITIONAL_ARGUMENTS_STORE_VARIABLES[${i}]}\t\t${POSITIONAL_ARGUMENTS_HELP_MESSAGES[${i}]}"
    done
}

print_arguments_usage_message() {
    for i in ${!OPTIONAL_ARGUMENTS_STORE_VARIABLES[*]}; do
        echo -en "[${OPTIONAL_ARGUMENTS_NAMES[${i}]}) ${OPTIONAL_ARGUMENTS_STORE_VARIABLES[${i}]}]"
        echo -n " "
    done
    for i in ${!POSITIONAL_ARGUMENTS_STORE_VARIABLES[*]}; do
        echo -en "${POSITIONAL_ARGUMENTS_STORE_VARIABLES[${i}]}"
        echo -n " "
    done
    echo
}

parse_arguments() {
    local positional_arguments_count=0
    while (($# != 0)); do
        argument=${1}
        if [[ ${argument} == "--"* ]]; then
            index=$(index_of OPTIONAL_ARGUMENTS_NAMES "${argument}")
            if [[ "${index}" != "" ]]; then
                shift
                argument=${1}
                eval "${OPTIONAL_ARGUMENTS_STORE_VARIABLES[${index}]}=${argument}"
            else
                log -ent "Option ${argument} is not declared!"
                exit 1
            fi
        else
            if ((${positional_arguments_count} < ${#POSITIONAL_ARGUMENTS_STORE_VARIABLES[@]})); then
                eval "${POSITIONAL_ARGUMENTS_STORE_VARIABLES[${positional_arguments_count}]}=${argument}"
                positional_arguments_count=$((${positional_arguments_count} + 1))
            else
                log -ent "Too many positional arguments!"
                exit 1
            fi
        fi
        shift
    done

    for i in ${!OPTIONAL_ARGUMENTS_STORE_VARIABLES[*]}; do
        if [[ "${!OPTIONAL_ARGUMENTS_STORE_VARIABLES[${i}]}" == "" ]]; then
            eval "${OPTIONAL_ARGUMENTS_STORE_VARIABLES[${i}]}=${OPTIONAL_ARGUMENTS_DEFAULT_VALUES[${i}]}"
        fi
    done
}

index_of() {
    local array=${1}[@]
    local value=${2}
    local index=0

    for element in ${!array}; do
        if [[ ${element} == ${value} ]]; then
            echo ${index}
            return 0
        fi
        index=$((index + 1))
    done
    return 1
}

test_names() {
    parse_arguments --a-flag "a-value" "c_value" "d_value" "e_value" "f_value"
    echo ${a} ${b} ${c} ${d} ${e}
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    register_optional_argument "--a-flag" "a" "a_value" "this is simple a optional argument"
    register_optional_argument "--b-flag" "b" "b_value" "this is simple b optional argument"
    register_positional_argument "c" "this is simple c positional argument"
    register_positional_argument "d" "this is simple d positional argument"
    register_positional_argument "e" "this is simple e positional argument"

    test_names
    print_arguments_help_message
    print_arguments_usage_message
fi