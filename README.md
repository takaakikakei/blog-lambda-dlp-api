# blog-lambda-dlp-api

AWS Lambda から DLP API を使ってみたブログ用

# デプロイ

## 事前準備

### Cloud Data Loss Prevention (DLP) API の有効化

Google Cloud コンソールで Cloud Data Loss Prevention (DLP) API の画面を開き、「有効にする」をクリックし、API を有効化します。

### DLP API コールに必要なサービスアカウントの作成

以下のブログを参考にサービスアカウントを作成します。

[AWS Lambda からサービスアカウントで Google APIs を叩くまでにやったこと \| DevelopersIO](https://dev.classmethod.jp/articles/call-google-apis-from-aws-lambda-by-service-account/#toc-3)

### AWS Systems Manager のパラメータストアの設定

デプロイリージョンの AWS Systems Manager のパラメータストアに、以下のパラメータを作成

- /ステージ名/GCP_PROJECT_ID
  - GCP の利用プロジェクト ID
- /ステージ名/GCP_CREDENTIALS_JSON
  - サービスアカウト作成時にダウンロードした JSON の文字列

## パッケージやライブラリのインストール

- 下記のコマンドでパッケージやライブラリのインストール

```bash
npm ci
pipenv install
```

## Serverless Framework を使ってデプロイ

```bash
sls deploy --stage ステージ名
```
