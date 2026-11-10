# firmware

STM32CubeMX で生成したプロジェクトを VS Code でビルドします。

## 構成

```
firmware/
├── <project>.ioc     # CubeMX の設定ファイル（ピン・クロック・周辺機能）
├── Core/, Drivers/   # CubeMX が自動生成するコード（基本的に編集しない）
├── CMakeLists.txt    # CubeMX が生成するビルド設定
└── app/              # 自分たちで書くコード（初心者はここだけ触ればOK）
    ├── drivers/      #   モータ・エンコーダ・壁センサ・IMU など
    ├── control/      #   速度・位置の制御
    └── maze/         #   迷路探索・経路計算
```

CubeMX でコードを再生成すると `Core/` の内容が上書きされることがあるため、
自分で書くコードはできるだけ `app/` に置き、`Core/` の `USER CODE BEGIN` 〜 `END` の中から呼び出すだけにします。

## ビルドと書き込み

TBD（[開発環境の構築](../docs/getting-started.md) を参照）
