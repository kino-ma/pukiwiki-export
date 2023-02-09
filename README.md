# pukiwiki-to-growi

Converter utility to import pukiwiki data to growi.

Because both software are mainly use in Japan, this readme is written in English.

## 本ツールについて

Pukiwiki の Wiki データをダンプして Growi にインポートできるようにするツールです。  
ただし、一部非公式な手法を用いているため、一切の動作保証をしません。ご利用は自己責任でお願いいたします。

## 使い方

エクスポート元の Pukiwiki を pukiwiki.example.com、 インポート先の Growi を growi.example.com とします。

### 1. Pukiwiki データをエクスポートする

1. pukiwiki.example.com/index.php?cmd=dump を開きます。データをダンプするための画面が現れます。
2. `エンコードされているページ名をディレクトリ階層付きのファイルにデコード ` にチェックを **入れず**、 OK ボタンを押します。
3. 好きなパスを指定し、ダウンロードします。
