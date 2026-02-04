# ITコンサルティング会社向け基幹システム (Mock)

ITコンサルティング会社の社内基幹システムを想定したモックアップアプリケーションです。
Python (FastAPI) と Tailwind CSS を使用し、Docker環境で即座に動作確認ができるように構築されています。

## 特徴

*   **プロジェクト管理**: 案件のステータス、契約金額、期間などを一覧管理
*   **リソース管理**: コンサルタント（社員）のアサイン状況、稼働率（稼働/ベンチ）の可視化
*   **モダンなUI**: Tailwind CSS を採用したシンプルでレスポンシブな画面
*   **ダミーデータ生成**: 起動時にリアルなダミーデータ（社員50名、顧客、プロジェクト）を自動生成

## 技術スタック

*   **Backend**: Python 3.11, FastAPI, SQLAlchemy
*   **Frontend**: Jinja2 Templates, Tailwind CSS (CDN)
*   **Database**: SQLite (ファイルベース)
*   **Container**: Docker, Docker Compose
*   **Package Manager**: uv (pyproject.toml)

## 起動方法

Docker と Docker Compose が必要です。

```bash
# ビルドと起動
docker-compose up --build
```

起動後、ブラウザで以下のURLにアクセスしてください。

*   ダッシュボード: http://localhost:8000
*   リソース一覧: http://localhost:8000/employees

## ディレクトリ構成

*   `app/`: アプリケーションコード
    *   `models.py`: データベース定義 (SQLAlchemy)
    *   `main.py`: ルーティングとビューロジック
    *   `templates/`: HTMLテンプレート (Jinja2)
    *   `seed.py`: ダミーデータ生成スクリプト
*   `Dockerfile`: コンテナ定義
*   `docker-compose.yml`: コンテナオーケストレーション設定
