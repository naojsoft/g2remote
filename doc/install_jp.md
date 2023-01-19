# 推奨される動作環境

## 全OS共通

* 大きなウィンドウが表示可能な高解像度モニター。Apple Retina displayで使用されているHiDPIスクリーンなど。
* sshクライアントが使えるコマンドライン環境
* 鍵認証を設定できること (e.g. `ssh-keygen`など。通常ではsshクライアントと共にインストールされています)
* 自分でパッケージをインストールできるPython3.7以上の環境。Miniconda又はAnacondでの使用を推奨。
* HTML5対応のWebブラウザ。　サポートされているのブラウザは、Firefox,Chrome,SafariとEdgeです。

## Windows（補足）

* Windows 10はOpenSSHがインストールされていますが、使用するには機能を有効にする必要があるかもしれません。下記の場所に移動して、

  設定->アプリ->オプション機能の管理

  表示されるリストにOpenSSHが含まれていることを確認してください。もしリストに含まれていなければ、"オプション機能の管理"を押して、OpenSSHを"オプション機能"リストに追加してください。

# インストール方法

すでに仮想環境がある場合は、他の環境への影響を避けるために、Python3.7以上の別の仮想環境を作成してください。
"subaru-gers"という名で、新たな仮想環境を構築する場合は：

```bash
$ conda create -n subaru-gers python=3.10
```

Conda activateコマンドで、新たに作成したPython仮想環境を利用し、 "git"と"paramiko"パッケージをインストールします。

```bash
$ conda activate subaru-gers
(subaru-gers)$ conda install git paramiko
```

その後g2remoteをインストールします。

```bash
(subaru-gers)$ pip install git+https://github.com/naojsoft/g2remote
```

このコマンドはg2remoteをダウンロード、インストールすると同時に、必要なPythonパッケージもインストールします。
*上記のように"paramiko"をconda installする事を推奨します。pip installをするとOSによりインストールトラブルが起こる可能性があります。


## 操作方法

[こちら](https://github.com/naojsoft/g2remote/blob/master/doc/operation_jp.md)のファイルをご覧ください。


## ダウンロード

* 全ユーザー：Python3.7以上のシステム環境をお使いください。(不明な場合は、、Minicondaのインストールを推奨します。ダウンロードは[こちら](https://docs.conda.io/en/latest/miniconda.html)です。

