#!/bin/bash

set -euo pipefail

function main() {
    setup_vars
    change_dir

	check_python_venv
    check_install_dir
    check_spacy_models

    generate_python_from_proto

    tidy_up
}

function check_python_venv() {
	set +u
	if [[ "${VIRTUAL_ENV}" = "" ]]; then
		echo 'Cannot detect $VIRTUAL_ENV for Python. Quitting!'
		exit 1
	fi
	set -u
}

function check_spacy_models() {
    num_models=$(python -c 'from spacy.util import get_installed_models; print(len(get_installed_models()))' 2>/dev/null) || {
		echo "Couldn't load spacy, is it installed?"
		exit 1
	}
    echo "Checking SpaCy models..."
    if [[ num_models -eq 0 ]]; then
        read -p "SpaCy couldn't find any models. Do you want to install the '${model_name}' model? [Y/n] " response
        if [[ "${response}" = "y" ]] || [[ "${response}" = "Y" ]] || [[ "${response}" = "" ]]; then
            python -m spacy download "${model_name}"
        fi
    fi
}

function generate_python_from_proto() {
    "${this_dir}"/generate.sh
}

function tidy_up() {
    popd &>/dev/null
}

function change_dir() {
    pushd "${wd}" &>/dev/null
}

function setup_vars() {
    this_dir=$(realpath $(cd -- $(dirname -- "${BASH_SOURCE[0]}") &> /dev/null && pwd))
    wd=$(realpath "${this_dir}/../")
    install_dir="${HOME}/spacy-service"
    default_model_name="en_core_web_lg"
    model_name="${default_model_name}"
}

function check_install_dir() {
    if [[ ! -r "${install_dir}" ]]; then
        read -p "${install_dir} does not exist, create now? [y/N] "  response
        if [[ "${response}" = "y" ]]; then
            mkdir -p "${install_dir}"
        else
            echo "Quitting."
            exit 0
        fi
    fi
}

main "${@}"
