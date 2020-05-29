# 使用方法

ここでは、g2remoteパッケージはすでにお使いの環境下でインストールされているとします。インストールについては[こちら](https://github.com/naojsoft/g2remote/blob/master/install.md)をご確認ください。

## 初回利用時のみ

1). SSH公開鍵認証設定を以下のように(もしくはご自分のsshクライアントの提供する方法で)行ってください。

```bash
$ ssh-keygen -b 4096 -f gen2_connect
```

上記の操作で、`gen2_connect`(秘密鍵)と`gen2_connect.pub`(公開鍵)の2つのファイルが生成されます。**この際、パスフレーズは設定しないでください。** パスフレーズを設定するとプログラムが正しく動作しません。ファイル作成後、ハワイ観測所の所定連絡先まで、お名前、所属機関名、リモート観測の日時とともに、`gen2_connect.pub`をお送りください。

注意：この操作は、g2remoteを使って初めてリモート観測を行う場合に必要です。次回以降は、観測所からの依頼がない限り、`gen2_connect.pub`の生成と提出は不要ですので、公開鍵を提出済みである旨をメールでお知らせください。

## 観測前の準備

2). 観測所より`config.yml`と`g2vncpasswd`の2つのファイルを受け取っていることをご確認ください。2つのファイルは同じフォルダに設置することを推奨します。

`config.yml`の中身を見て、以下のキーの値が正しいことをご確認ください。
* `vnc_passwd_file`： お受け取りになった`g2vncpasswd`ファイルへのパス
* `ssh-key`：上記の1)で作成したファイルのうち、".pub" ではない方のファイル(秘密鍵)へのパス

もし値が違っている場合、また変更するよう指示のあった場合には、`config.yml`をテキストエディタ等で開いて修正してください。

3). Pythonの動作するコマンドシェルを開いて、`g2remote`をインストールしたPython環境を起動してください。

4). シェル内で、以下のコマンドを実行してください。

```bash
$ g2connect -f config.yml
```

`g2connect>`プロンプトが表示されます。

5). 以下のように、"c"コマンドを実行して接続してください。接続に成功すると、コマンドプロンプトに戻ります。

```bash
g2connect> c
connecting ...
g2connect> 
```

6). スクリーン番号の1から8を入力して、VNCスクリーンを開いてください。各スクリーンの表示する情報は以下をご覧ください。

7). 観測終了時には、開いているVNCスクリーンを閉じて、コマンドプロンプトで"q"を押してください。


## 注意事項

* 複数ディスプレイをお持ちでない場合は、仮想デスクトップにVNCスクリーンを配置することも可能です。

* 複数の接続先をお持ちの場合、各ホストで`g2connect`を利用して複数のスクリーンを表示することが可能です。(1つのホストにつき2つのターミナルが必要です。)

## VNCスクリーン

| Screen | Content |
| ------ | ------- |
| 1      | hskymon (observation planning tool) |
| 2      | instrument control GUIs |
| 3      | integgui2 (observation execution tool) |
| 4      | fitsview (QDAS, quick look, slit alignment, etc), HSC obslog |
| 5      | guideview (guiding control and monitoring) |
| 6      | statmon (current telescope status) |
| 7      | instrument control and monitoring GUIs |
| 8      | instrument control and monitoring GUIs |

各スクリーンのウィンドウサイズは2550x1380です。リモート観測時に必ずしも全てのスクリーンを確認する必要はないかもしれません。当該観測でどのスクリーンに注目するべきか、担当のサポートアストロノマーにご相談ください。
