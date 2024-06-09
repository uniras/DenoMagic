# Deno Magic Command

## 概要

Jypyter(notebook/lab)またはGoogle ColabのコードセルにDeno(JavaScript/TypeScript)を書いて実行するためのマジックコマンドです。

## インストール

denomagic.pyをダウンロードして、Jupyterの場合は使用するノートブックと同じディレクトリに、
Google Colabの場合は/contentディレクトリまたはGoogle DriveのColab Notebooksディレクトリ(/content/drive/MyDrive/Colab Notebooks/)にアップロードしてください。

## 使い方

### マジックコマンドの追加

コードセルに以下のコードを貼り付けて実行しマジックコマンドを登録してください。カーネルやランタイムを再起動する度に再実行する必要があります。

```python
!pip install denomagic
from denomagic import install_deno_colab, register_deno_magics

# denoのインストール(Google Colab用、他の環境では無視されます
install_deno_colab()
# マジックコマンドの登録
register_deno_magics()
```

### マジックコマンドの使い方

コードセルの冒頭に以下のようにマジックコマンドを記述してください。実行するとDenoによってコードセル内のJavaScript/TypeScriptコードが実行されます。

```javascript
%%run_deno

console.log("Hello, world!");
```

また、コードセルのJavaScript/TypeScriptコードをDenoでトランスパイルしてiframe内で実行するマジックコマンドも用意しています。
以下は、ブラウザ用のライブラリであるp5.jsを使った例です。

```javascript
%%run_deno_iframe 830 430
import "https://cdn.jsdelivr.net/npm/p5@1.9.4/lib/p5.js";

const sketch = (p: any) => {
  let x = 0;
  let y = 0;
  let speed = 2;
  let color: [number, number, number] = [0, 0, 0];

  p.setup = () => {
    p.createCanvas(800, 400);
    x = p.width / 2;
    y = p.height / 2;
  };

  p.draw = () => {
    p.background(220);
    p.fill(color);
    p.ellipse(x, y, 50, 50);
    if (p.keyIsDown(p.LEFT_ARROW) === true) {
      x -= speed;
    }

    if (p.keyIsDown(p.RIGHT_ARROW) === true) {
      x += speed;
    }

    if (p.keyIsDown(p.UP_ARROW) === true) {
      y -= speed;
    }

    if (p.keyIsDown(p.DOWN_ARROW) === true) {
      y += speed;
    }
  };

  p.mousePressed = () => {
    color = [p.random(255), p.random(255), p.random(255)];
  };
};

new p5(sketch);
```

### マジックコマンド

#### %%run_deno

コードセル内のJavaScript/TypeScriptをDenoで実行します。
引数はありません。

#### %%run_deno_iframe

コードセル内のJavaScript/TypeScriptをDenoでトランスパイルしてiframe内で実行します。

```jupyter
%%run_deno_iframe [width] [height] [srcs]
```

- width: iframeの幅を指定します。デフォルトは500です。
- height: iframeの高さを指定します。デフォルトは500です。
- srcs: 外部JavaScriptのURLを指定します。複数指定する場合はスペースで区切ります。

#### %%run_deno_bundle_iframe

コードセル内のJavaScript/TypeScriptをimportしたコードも含めてトランスパイル及びバンドルしてiframe内で実行します。

引数は%%run_deno_iframeと同じです。

#### %%view_deno_iframe

コードセル内のJavaScript/TypeScriptをDenoでトランスパイルした後生成したHTMLを出力します。

引数は%%run_deno_iframeと同じです。

#### %%view_deno_bundle_iframe

コードセル内のJavaScript/TypeScriptをimportしたコードも含めてトランスパイル及びバンドルした後生成したHTMLを出力します。

引数は%%run_deno_iframeと同じです。
