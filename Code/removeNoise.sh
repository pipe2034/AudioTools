if [ "$#" = 3 ]; then
	python3 enhance_jit.py "$1" "$2" "$3"
else
	echo 'Error'
	echo 'Número de argumentos invalido'
fi
