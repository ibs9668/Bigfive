依赖：scws，libsvm

scws：

基于python2，python3会报错
8、安装scws
	版本：SCWS-1.2.3

(1). 取得 scws-1.2.3 的代码
wget http://www.xunsearch.com/scws/down/scws-1.2.3.tar.bz2
	

(2). 解开压缩包
tar xvjf scws-1.2.3.tar.bz2
	

(3). 进入目录执行配置脚本和编译
cd scws-1.2.3
./configure --prefix=/usr/local/scws

make

make install


(4). 字典配置
cd /usr/local/scws/etc

需要注意的是修改文件权限：
wget?http://www.xunsearch.com/scws/down/scws-dict-chs-utf8.tar.bz2
		wget?http://www.xunsearch.com/scws/down/scws-dict-cht-utf8.tar.bz2
tar xvjf scws-dict-chs-utf8.tar.bz2

tar xvjf scws-dict-cht-utf8.tar.bz2

sudo chmod 664 dict_cht.utf8.xdb

sudo chmod 664 dict.utf8.xdb
	

(5). 安装pyscws：
git clone https://github.com/MOON-CLJ/pyscws.git
cd pyscws

python setup.py install
路径设置（保证import scws不报错）：在gedit /etc/ld.so.conf中添加一行/usr/local/scws/lib/，然后sudo ldconfig


python3版本：
参照
https://github.com/xyanyue/python3_scws

仍然是先安装scws的c版本
然后使用setup.py直接安装，注意需要找好python3的include包的文件夹并在scws.c的头文件中改好，然后再运行命令编译和导入
上面的安装部分稍微有点莫名奇妙，总之这个东西比较玄学，可以多试试，但是最简单的还是造好setup.py了


libsvm：
一、下载：
网址：http://www.csie.ntu.edu.tw/~cjlin/libsvm/oldfiles/
，选择libsvm-3.22.tar.gz

二、解压：
tar -zxvf libsvm-3.22.tar.gz

三、编译：
打开终端，
1. 进入libsvm-3.22目录下，执行make；

2. 进入libsvm-3.22/python
 子目录下，执行make。
四、使用
从libsvm-3.22/python
调用svmutil即可