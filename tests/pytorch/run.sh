pythons=("3.6" "3.7" "3.8" "3.9")
torches=("1.7.1+cu110" "1.8.0+cu111" "1.8.1+cu111" "1.9.0+cu111" "1.10.2+cu111")

_get_tag() {
  python=$1
  torch=$2
  echo "python-${python}-torch-${torch}" | tr '+' '_'
}

_build() {
  for python in "${pythons[@]}"; do
    for torch in "${torches[@]}"; do
      tag=$(_get_tag ${python} ${torch})
      echo "Building tag ${tag}"

      docker build \
        --build-arg PYTHON="${python}" \
        --build-arg PYTORCH="${torch}" \
        --tag ${tag} \
        .
    done
  done
}

_run() {
  for python in "${pythons[@]}"; do
    for torch in "${torches[@]}"; do
      tag=$(_get_tag ${python} ${torch})
      echo "Running tag ${tag}"
      docker run --gpus 0 -it ${tag}
    done
  done
}

_submit() {
  if [ "$#" -lt 1 ]; then
    echo "Usage: sh run.sh submit <submission-file>"
    exit
  fi

  out=$1
  rm -f ${out}

  for python in "${pythons[@]}"; do
    for torch in "${torches[@]}"; do
      tag=$(_get_tag ${python} ${torch})
      submission=$RANDOM
      echo "Submitting tag ${tag} as submission ${submission}"

      naacl-utils submit ${tag} ${submission}
      echo ${tag} ${submission} >> ${out}
    done
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