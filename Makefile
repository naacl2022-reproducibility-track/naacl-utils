.PHONY : test-run
test-run :
	docker pull nvidia/cuda:11.0-base
	naacl-utils submit nvidia/cuda:11.0-base cuda-run-2 --cmd nvidia-smi
