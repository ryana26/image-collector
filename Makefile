installer:
	rm -rf dist build
	pyinstaller saver.py --name image-collector
	cp config.yaml dist/image-collector
	cp upload.sh dist/image-collector
	cp desktop_maker.sh dist/image-collector
	mkdir -p packaging/deb/image-collector/usr/local
	mkdir dist/image-collector/images
	mkdir dist/image-collector/images/grapes dist/image-collector/images/tomatoes
	chmod -R 775 dist/image-collector/images
	cp -R images/desktop_icon.png images/desktop_icon.png dist/image-collector/images
	rm -rf packaging/deb/image-collector/usr/local/image-collector
	cp -R dist/image-collector packaging/deb/image-collector/usr/local

deb-package:
	make clean
	make installer
	cd packaging/deb && dpkg-deb --build image-collector && mv image-collector.deb image-collector-1.0-amd64.deb

requirements:
	sudo apt install python3 python3-pip python3-venv python3-tk
	pip3 install -r requirements.txt
	pip3 install pyinstaller
	echo "Please reboot your system as pyinstaller does not immediately appear in path."

clean:
	rm -rf dist build
