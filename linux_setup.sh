pip3 install pandas_ta ccxt pandas numpy scipy backtesting matplotlib
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
sudo ./configure
sudo make
sudo make install
pip3 install ta-lib
cd ..
rm -rf ta-lib-0.4.0-src.tar.gz
rm -rf ta-lib/
echo "Done installing dependencies"