all: file-bugs

file-bugs: maint.pickle
	./get-maint-bugs.py $<

maint.pickle:
	./get-all-maints.py > $@
