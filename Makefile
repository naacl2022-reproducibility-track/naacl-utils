.PHONY : docs
docs :
	@cd docs && make html && open build/html/index.html
