# pukiwiki-to-growi

Converter utility to import pukiwiki data to growi.

Because both software are mainly use in Japan, this README document is written in English.

## 本ツールについて

Pukiwiki の Wiki データをダンプして Growi にインポートできるようにするツールです。  
インポートの際、 Pukiwiki 記法から Markdown 記法への変換を行います。

ただし、一部非公式な手法を用いているため、一切の動作保証をしません。ご利用は自己責任でお願いいたします。

## 機能

- Pukiwiki ダンプデータを Growi アーカイブデータに変換します
- Pukiwiki 記法から Markdown 記法への変換を行います
    - 対応する記法 
        - `[#hash]` の削除
        - `** 見出し` の変換 (h1〜h3)
        - `-- 箇条書き` の変換
        - `&br` の変換
        - `#pre{コードブロック}` の変換
        - `%%打ち消し線%%` の変換
        - `#lsx` の変換
    - Wiki 内リンク、テーブルなど、非対応の記法があります
    - 変換方法等、詳しくは [`lib/pukiwiki.py`](lib/pukiwiki.py) をご覧ください
    - (参考: https://qiita.com/yuki-takei/items/152e20f4421333ae8fd9)
- アーカイブデータには `pukiwiki` (または任意のユーザ名) ユーザが含まれ、インポートされたページはこのユーザによって作成されたことになります
- インポートされるページには、任意のプレフィックスを付与することができます
    - デフォルトでは `pukiwiki` となります

## 環境

動作確認環境

- Pukiwiki 1.5.1
- Growi 5.0.2

動作環境

- Python 3.10
- または Nix Flakes
    - 開発用シェル (`$ nix develop`) 内でご使用ください

## 使い方

エクスポート元の Pukiwiki を pukiwiki.example.com、 インポート先の Growi を growi.example.com とします。

### Step 1. Pukiwiki データをエクスポートする

1. pukiwiki.example.com/index.php?cmd=dump を開きます。データをダンプするための画面が現れます。
2. `〜.tar 形式` にチェックをつけます。
3. `エンコードされているページ名をディレクトリ階層付きのファイルにデコード ` の **チェックが外れている** ことを確認します。
4. OK ボタンを押します。
5. 好きなパスを指定し、ダウンロードします。

### Step 2. Pukiwiki データを Growi のインポート形式に変換する

Growi は、あるインスタンスから別のインスタンスへ移行をするための import/export インタフェースを備えています。本ツールは、それを利用してインポートを行います。

1. 本リポジトリをクローンします。
2. Step 1. でエクスポートしたデータのパスと、任意の出力先ファイル名を指定し、 `convert.py` を実行します。
    - `python3 convert.py dump.tar.gz`
    - その他のオプションについては `-h` オプションで参照してください
3. `export.growi.zip` または任意のファイル名の Zip ファイルが生成されていることを確認します

### Step 3. データを Growi にインポートする

先ほどエクスポートしたデータをインポートします。

1. 管理者アカウントで Growi にログインします。
2. `growi.example.com/admin/app` から、メンテナンスモードを有効化します。
3. `growi.example.com/admin/importer` からエクスポートした Zip ファイルをアップロードします。
4. Pages, Revisions, Users 全てにチェックをつけます。
5. Pages, Revisions, Users 全てに対し、 `Insert` となっているプルダウンを `Upsert` に変更します。
   - `Insert` ではエラーが発生し、インっポートに失敗します
6. 「インポート」ボタンを押します。
7. `growi.example.com/admin/app` から、メンテナンスモードを解除します。
8. トップページに戻り、 `/pukiwiki` または任意のパスプレフィックス以下に Pukiwiki でエクスポートしたページが表示されていることを確認します。


## 参考

- [Pukiwikiの文書をエクスポートして、textile形式に変換し、RedmineWikiに移行する - Qiita](https://qiita.com/carbonss/items/d91297ffdd069cf27f30)
- [PukiWiki の文書を Markdown に変換するワンライナー(一部 crowi-plus 仕様) - Qiita](https://qiita.com/yuki-takei/items/152e20f4421333ae8fd9)