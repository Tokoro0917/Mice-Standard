# hardware

KiCad の回路図・基板データです。

| ディレクトリ | 内容 |
| --- | --- |
| `main-board/` | KiCad プロジェクト（`.kicad_pro`, `.kicad_sch`, `.kicad_pcb`） |
| `lib/` | 標準機で使うシンボル・フットプリント・3D モデル |
| `production/` | 発注用データ（ガーバー、BOM、部品配置）。リリースごとに更新 |

基板は役員がまとめて発注します。部員ははんだ付けの際に `production/` の BOM を参照してください。
