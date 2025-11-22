# タスク

- [x] Flask プロジェクト構造と初期ファイルを設定する。（`app/__init__.py`、`run.py` を参照）
- [x] データベースを初期化する。（データベースモデルと CLI は `app/models.py`、`app/cli.py`）
- [x] テストフレームワーク（pytest）を整備する。
    - [x] テストライブラリ（pytest、pytest-flask）をインストールする。
    - [x] 基本的なテストファイルを作成する（例: `tests/test_basic.py`）。
    - [x] pytest を実行してセットアップを確認する。（`pytest`）
- [x] ユーザー登録とログイン機能を実装する。（`app/routes.py`、フォームは `app/forms.py`）
- [x] 認証のテスト（登録、ログイン、ログアウト）を書く。（`tests/test_auth.py`）
- [x] ナビゲーション付きの基本レイアウトを作成する。（`app/templates/`）
- [x] 予定表のメインカレンダービューを実装する。（`app/routes.py::calendar`、テンプレートは `app/templates/calendar.html`）
- [x] スケジュールの作成および編集機能を実装する。（`app/routes.py::create_schedule`、`app/routes.py::edit_schedule`）
- [x] スケジュール CRUD 操作のテストを書く。（`tests/test_calendar.py`）
- [x] スケジュール削除機能を実装する。（`app/routes.py::delete_schedule`）
- [x] 会議室管理（CRUD）を実装する。（`app/routes.py` の部屋エンドポイント）
- [x] 会議室管理のテストを書く。（`tests/test_rooms.py`）
- [x] チームスケジュール共有機能を実装する。（`app/models.py` の `Schedule.participants`、スケジュールのフォーム／ルート）
- [x] 共有機能のテストを書く。（`tests/test_calendar.py::test_shared_schedule_visible_to_participant`）
- [x] 週間プランナー再設計の要件を文書化する。（`README.md`、`docs/`）

## 今後の作業

- [x] 曜日を横方向、時間を縦方向に表示する週間プランナーテンプレートを実装する。（`app/templates/calendar.html` を更新し、`app/templates/partials/` にパーシャルを追加）
    - [x] 曜日ごとの列と設定から取得した時間帯の行で 7 日分のグリッドを生成するようにカレンダービューの HTML を再構成する。
    - [x] イベントをグリッド内に配置し、重なりを視覚的に区別するため、`app/static/css/` に CSS モジュールを追加する。
- [x] カレンダールートから週間プランナー向けのスケジュールデータを公開する。（イベントを曜日／時間帯ごとに整理するヘルパーを `app/routes.py::calendar` で調整）
- [x] プランナーのキーボード操作と ARIA ラベリングを提供する。（テンプレートのセマンティクスを強化し、`docs/weekly_planner_design.md` にガイドを追加）
- [x] タブレットとモバイル向けのレスポンシブ調整を追加する。（プランナーのスタイルシートにメディアクエリを拡張）
- [x] 新しいレイアウト向けの自動テストを拡充する。（`tests/test_calendar.py` にビューのテストを追加し、必要に応じてスナップショットデータを調整）
- [x] SQLAlchemy 2.0 に合わせて `Query.get`/`get_or_404` の使用をセッション API に置き換え、警告を解消する。（`app/models.py`、`app/routes.py`、`tests/`）

## 今回の作業

- [x] README.md、REQUIREMENTS.md、TASKS.md、および `docs/` 配下の Markdown ドキュメントを日本語に翻訳する。
