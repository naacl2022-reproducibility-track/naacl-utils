tfs=("2.4.0" "2.5.0" "2.6.0" "2.7.0")

_get_tag() {
  tf=$1
  echo "tf-${tf}"
}

_build() {
  for tf in "${tfs[@]}"; do
    tag=$(_get_tag ${tf})
    echo "Building tag ${tag}"

    docker build \
      --build-arg TENSORFLOW="${tf}" \
      --tag ${tag} \
      .
  done
}

_run() {
  for tf in "${tfs[@]}"; do
    tag=$(_get_tag ${tf})
    echo "Running tag ${tag}"
    docker run --gpus 0 -it ${tag}
  done
}

_submit() {
  if [ "$#" -lt 1 ]; then
    echo "Usage: sh run.sh submit <submission-file>"
    exit
  fi

  out=$1
  rm -f ${out}

  for tf in "${tfs[@]}"; do
    tag=$(_get_tag ${tf})
    submission=$RANDOM
    echo "Submitting tag ${tag} as submission ${submission}"

    naacl-utils submit ${tag} ${submission}
    echo ${tag} ${submission} >> ${out}
  done
}

_verify() {
  if [ "$#" -lt 1 ]; then
    echo "Usage: sh run.sh verify <submission-file>"
    exit
  fi

  inp=$1
  while read tag submission; do
    echo "Verifying ${tag} with submission ${submission}"
    naacl-utils verify ${submission} expected.txt
  done < ${inp}
}

if [ "$#" -lt 1 ]; then
    echo "Usage: sh run.sh <command>"
    exit
fi

command=$1
if [ "${command}" = "build" ]; then
  _build
elif [ "${command}" = "run" ]; then
  _run
elif [ "${command}" = "submit" ]; then
  out=$2
  _submit ${out}
elif [ "${command}" = "verify" ]; then
  inp=$2
  _verify ${inp}
fi