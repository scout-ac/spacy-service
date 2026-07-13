#!/bin/bash

set -euo pipefail

this_dir=$(realpath $(cd -- $(dirname -- "${BASH_SOURCE[0]}") &> /dev/null && pwd))
wd=$(realpath "${this_dir}/../")

dest="${wd}/spacy_service/generated/"

cd "${wd}" &>/dev/null

echo "Generating GRPC code for Python..."

# Rename original file to temp file.
t=$(mktemp -p ./proto -t XXXXXXXX.proto)
mv proto/spacy_service.proto "${t}"

# Strip Go-specific fields, producing Python-specific version of original.
sed -re 's|,\s? \(go.field\)\.name[^]]+||g' "${t}" > proto/spacy_service.proto

while read line ; do
    echo "    ${line}" | sed -re 's,Writing ,Writing '"${dest}"',g'
done < <(
    python \
        -m grpc_tools.protoc \
        --proto_path=./proto \
        --python_betterproto_opt=typing.310 \
        --python_betterproto_out="${dest}" \
        --grpc_python_out="${dest}" \
        proto/spacy_service.proto \
        2>&1
)

# Restore original.
mv -f "${t}" proto/spacy_service.proto

################################################################################
# Yuck. Hacks follow.
################################################################################

pushd "${dest}" &>/dev/null

# Ensure filename compatability with protoc defaults.
if [[ ! -r spacy_service.py ]]; then
	echo "Could not find file spacy_service.py, quitting!" >&2
	exit 1
fi

echo "Renaming: spacy_service.py  ->  spacy_service_pb2.py"
mv spacy_service.py spacy_service_pb2.py


if [[ ! -r spacy_service_pb2_grpc.py ]]; then
	echo "Could not find file spacy_service_pb2_grpc.py, quitting!" >&2
	exit 1
fi

# See https://github.com/grpc/grpc/issues/29459
echo "Tweaking import."
sed -i'' -r -e 's/^import spacy_service/from spacy_service.generated import spacy_service/g' spacy_service_pb2_grpc.py

popd &>/dev/null
echo "Done!"
