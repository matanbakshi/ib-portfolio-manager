change:
fetch-dependencies:
	mkdir -p bin/

	# Get chromedriver
	#curl -SL https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip > chromedriver.zip
	#unzip chromedriver.zip -d external_bin/

	wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
	tar xvjf phantomjs-2.1.1-linux-x86_64.tar.bz2 -C external_bin/
	mv external_bin/phantomjs-2.1.1-linux-x86_64/bin/phantomjs external_bin/phantomjs


	# Get Headless-chrome
	#curl -SL https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-37/stable-headless-chromium-amazonlinux-2017-03.zip > headless-chromium.zip
	#unzip headless-chromium.zip -d external_bin/

	# Clean
	#rm headless-chromium.zip chromedriver.zip
	rm phantomjs-2.1.1-linux-x86_64.tar.bz2
	rm external_bin/phantomjs-2.1.1-linux-x86_64/ -rf
