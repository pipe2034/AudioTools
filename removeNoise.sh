if [ "$#" = 3 ]; then
	python3 /home/daniel/Desktop/Gita/CLP/Preprocessing/clc-dns-challenge-2020/clcnet-dns2020/Code/enhance_jit.py "$1" "$2" "$3"
else
	echo 'Error'
	echo 'Número de argumentos invalido'
fi
