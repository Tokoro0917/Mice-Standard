# Mice-Standard

東京理科大学 Mice の **マイクロマウス標準機（クラシック）** をまとめたリポジトリです。
新入部員が「はんだ付けして、プログラムを書いて、走らせる」までを一通り体験できることを目指しています。

## 構成

| ディレクトリ | 内容 | ツール |
| --- | --- | --- |
| [`docs/`](docs/) | 環境構築、組み立て、はんだ付けの手順書 | Markdown |
| [`hardware/`](hardware/) | 回路図・基板データ | KiCad |
| [`mechanical/`](mechanical/) | 機構設計データ、3Dプリント・加工用データ | Fusion 360 |
| [`firmware/`](firmware/) | マイコンのプログラム | STM32CubeMX + VS Code |
| [`tools/`](tools/) | PC 側の補助ツール（ログ可視化など） | — |

## はじめかた

1. [開発環境の構築](docs/getting-started.md)
2. [はんだ付け](docs/soldering/README.md)
3. [組み立て](docs/assembly/README.md)
4. [プログラムを書き込んで動かす](firmware/README.md)

> 基板はサークルでまとめて発注します。部員の作業は **はんだ付けから** です。

## 仕様

| 項目 | 値 |
| --- | --- |
| 競技 | クラシック（18 cm 区画） |
| マイコン | TBD |
| モータ | TBD |
| センサ | TBD |
| 電源 | TBD |
| 寸法・重量 | TBD |

## バージョン

歴代の機体は残さず、**現行の標準機のみ** を管理します。
基板・機構・ファームの対応は Git のタグ（`v1.0` など）でそろえます。

## ライセンス

| 対象 | ライセンス |
| --- | --- |
| `firmware/`、`tools/`（プログラム） | [MIT License](LICENSE-MIT) |
| `hardware/`、`mechanical/`、`docs/` など（基板・CAD・文書） | [CC BY 4.0](LICENSE-CC-BY-4.0) |

どちらも「東京理科大学 Mice」のクレジットを書けば、改造・再配布・商用利用が可能です。
STM32CubeMX が生成するコードや、第三者のライブラリ・部品データは、それぞれ元のライセンスに従います。詳しくは [LICENSE](LICENSE) を参照してください。
