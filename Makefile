analysis:
	mkdir -p debug
	echo "== ident float_constant * ( return <= , float string != else int int_constant % for >= null - read = elif > def ) if < break & string_constant + { print } ] new [ ; /" > debug/terminais.txt
	python3 GIRLS.py $(DIR) $(PROGRAM)

clean:
	rm -rf __pycache__
	rm -rf debug
