#!/bin/bash

set -euo pipefail

this_dir=$(realpath $(cd -- $(dirname -- "${BASH_SOURCE[0]}") &> /dev/null && pwd))
wd=$(realpath "${this_dir}/../")

dest="${wd}/spacy_service/generated/"

cd "${wd}" &>/dev/null

echo "Generating GRPC code for Python..."

while read line ; do
    echo "    ${line}" | sed -re 's,Writing ,Writing '"${dest}"',g'
done < <(
    python \
        -m grpc_tools.protoc \
        --proto_path=./proto \
        --python_betterproto_opt=typing.310 \
        --python_betterproto_out="${dest}" \
        --grpc_python_out="${dest}" \
        proto/*.proto \
        2>&1
)

################################################################################
# Yuck. Hacks follow.
################################################################################

pushd spacy_service/generated &>/dev/null

# Ensure filename compatability with protoc defaults.
echo "Renaming: spacy_service.py  ->  spacy_service_pb2.py"
mv spacy_service.py spacy_service_pb2.py

# See https://github.com/grpc/grpc/issues/29459
sed -i'' -r -e 's/^import spacy_service/from spacy_service.generated import spacy_service/g' *pb2_grpc.py

popd &>/dev/null
