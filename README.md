print_label
==================

* CSVからはがきを印刷します
* 横書きと立て書きに対応しています
* Pillowが必要です

## 使い方

> print_label.py target_csv dest_dir [horizontal/vertical]

dest_dirに指定したディレクトリ配下に名前.pngというファイル名で画像が作成されます。

### 横書き

```
print_label.py data/sample.csv /tmp
```

### 縦書き

```
print_label.py data/sample.csv /tmp vertical
```

## 前提データ

* csvファイルはutf-8で保存する必要があります
* 苗字,名前,郵便番号,住所の順で作成します
* 郵便番号を同上とした場合は同居者とみなして、直近の宛名に連名処理します

## フォントについて

[はんなりフォント](http://typingart.net/?page_id=112)を利用させていただいております。フォントのラインセンスは[IPAフォントライセンス](http://ipafont.ipa.go.jp/ipa_font_license_v1-html)相当だそうです。


