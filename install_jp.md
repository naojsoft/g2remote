# 推奨される動作環境

## 全OS共通

* 解像度2550x1380のウィンドウを表示できる大型モニタ、もしくは複数台のモニタ(e.g. Apple Retina display)。1-2台の大型モニタを繋げた仮想デスクトップ環境も使用可能です。
* sshクライアントが使えるコマンドライン環境
* 公開鍵認証を設定できること (e.g. `ssh-keygen`など。通常ではsshクライアントと共にインストールされています)
* 自分でパッケージをインストールできるPython(3.7以上)環境 (e.g. Miniconda or Anaconda)
* `g2remote`のダウンロード (このパッケージです)

## Linux

* tigervnc viewer client プログラム (version 1.7.1以上、通常は"tigervnc-viewer"パッケージに含まれています)
* `vncpasswd` プログラム。(通常は"tigervnc-common"パッケージに含まれています)

## macOS

* "Screen Sharing" プログラム。  macOSには標準でインストールされています。

## Windows

* VNC viewer クライアントとして、"TightVNC"か"RealVNC"をお使いいただけます。
* Windows 10はOpen SSHを内蔵していますが、使用するには機能を有効にする必要があります。下記の場所に移動して、

  設定->アプリ->オプション機能の管理

  表示されるリストにOpenSSHが含まれていることを確認してください。もしリストに含まれていなければ、"オプション機能の管理"を押して、OpenSSHを"オプション機能"リストに追加してください。

# インストール方法

`g2remote` をインストールするには Python 3.7+ 環境を起動して、ダウンロード済みの`g2remote`フォルダに入り、setup.pyファイルのある階層で、以下を実行してください。
```bash
$ python setup.py install
```

実行と同時に、不足しているPythonパッケージもインストールされます。

## 操作方法

[こちら](https://github.com/naojsoft/g2remote/blob/master/operation_jp.md)のファイルをご覧ください。

## ダウンロード

* Windows ユーザー：
  * ご使用のOSに合った最新版をお使いください。(通常は64-bit版です)
  * 以下のサイトから"TightVNC"と"RealVNC"をダウンロードできます。
  * [TightVNCダウンロードサイト](https://github.com/TigerVNC/tigervnc/releases)
  * [RealVNC Viewer ダウンロードサイト](https://www.realvnc.com/en/connect/download/viewer/)
  * TightVNCについては、"Viewer"コンポーネントのみのインストールを推奨します。TightVNCインストーラの"Choose Setup Type"画面で、"Custom" オプションを選択してください。続いて、"Custom Setup"画面で、"TightVNC Server"のドロップダウンメニューの中から、"Extra feature will be unavailable"をお選びください。"TightVNC Server"のドロップダウンメニューが赤い"X"に変わります。

* 全ユーザー：Python3.7以上の環境でお使いください。(Pythonの経験のない方は、Minicondaの利用を推奨します。ダウンロードは[こちら](https://docs.conda.io/en/latest/miniconda.html)から可能です。)

