# 案件リソース管理用基幹システム (Mock)

Python (FastAPI) と Tailwind CSS を使用し、Docker環境で即座に動作確認ができるように構築されています。

## 特徴

*   **プロジェクト管理**: 案件のステータス、契約金額、期間、**粗利シミュレーション（予定原価・粗利率）**を管理
*   **リソース管理**:
    *   **稼働状況ヒートマップ**: 社員×月別の稼働率（向こう6ヶ月）を色分け表示
    *   **スキル検索**: 保有スキルや業界経験、氏名によるリアルタイム検索
*   **モダンなUI**: Tailwind CSS を採用したシンプルでレスポンシブな画面
*   **ダミーデータ生成**: 起動時にリアルなダミーデータ（社員50名、顧客、プロジェクト、**スキルタグ**）を自動生成

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
