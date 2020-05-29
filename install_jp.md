# 推奨される動作環境

## 全OS共通

* 解像度2550x1380のウィンドウを表示できる大型モニタ、もしくは複数台のモニタ(e.g. Apple Retina display)。1-2台の大型モニタを繋げた仮想デスクトップ環境も使用可能です。
* sshクライアントが使えるコマンドライン環境
* 公開鍵認証を設定できること (e.g. `ssh-keygen`など。通常ではsshクライアントと共にインストールされています)
* 自分でパッケージをインストールできるPython(3.5以上)環境 (e.g. Miniconda or Anaconda)
* `g2remote`のダウンロード (このパッケージです)

## Linux

* tigervnc viewer client プログラム (version 1.7.1以上、通常は"tigervnc-viewer"パッケージに含まれています)
* `vncpasswd` プログラム。(通常は"tigervnc-common"パッケージに含まれています)

## macOS

* "Screen Sharing" プログラム。  macOSには標準でインストールされています。

## Windows

* tigervnc viewer client プログラム。(version 1.7.1以上、通常は"tigervnc-viewer"パッケージに含まれています)
* `vncpasswd` プログラム。(通常は"tigervnc-common"パッケージに含まれています)


# インストール方法

`g2remote` をインストールするには Python 3.5+ 環境を起動して、g2remoteフォルダに入り、以下を実行してください。
```bash
$ python setup.py install
```

実行と同時に、不足しているPythonパッケージもインストールされます。

## 操作方法

[こちら](https://github.com/naojsoft/g2remote/blob/master/operation.md)のファイルをご覧ください。

## ダウンロード

* Windows ユーザー：こちらの[tigervnc公開サイト](https://github.com/TigerVNC/tigervnc/releases)から"tigervnc"と"vncviewer"をダウンロードできます。ご使用のOSに合った最新版をお使いください。

* 全ユーザー：Python3.5以上の環境でお使いください。(Pythonの経験のない方は、Minicondaの利用を推奨します。ダウンロードは[こちら](https://docs.conda.io/en/latest/miniconda.html)から可能です。)

