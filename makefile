all: cserver contestmeister contestant
	chmod +x cserver contestmeister contestant
cserver:
	echo "python3 server2.py" > cserver
contestmeister:
	echo "python3 contestMeister2.py \$$1 \$$2" > contestmeister
contestant:
	echo "python3 client2.py \$$1 \$$2" > contestant