# Deno Magic Command

## 概要

Jypyter(notebook/lab)またはGoogle ColabのコードセルにDeno(JavaScript/TypeScript)を書いて実行するためのマジックコマンドです。

## 使い方

### マジックコマンドの追加

コードセルに以下のコードを貼り付けて実行しマジックコマンドを登録してください。カーネルやランタイムを再起動する度に再実行する必要があります。

```python
%pip install denomagic
import denomagic

# denoのインストール(Google Colab用、他の環境では無視されます
denomagic.install_deno_colab()
# マジックコマンドの登録
denomagic.register_deno_magics()
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

```jupyter
%%run_deno [userval]
```

コードセル内のJavaScript/TypeScriptをDenoで実行します。

- userval: Jupyterのユーザー変数をDenoで利用するかどうかを設定します。デフォルトはFalseです。

usevalをTrueにすると、Jupyterのユーザー変数を`globalThis.jupyter`を通じて利用できるようになり、セルを超えた変数のやりとりが出来るようになります。  
内部ではJupyterとDenoの間をJSONの一時ファイルでやりとりしているため、JSONに変換できないオブジェクトは利用できません。  
利用した場合の動作は未定義です。

Jupyterのコードセル内で実行されている場合、`globalThis.isJupyterCell`が定義されているので、これが`undefined`ではないかどうかを確認することでJupyterのコードセルからの実行なのかどうかを判定できます。

Jupyterユーザー変数を利用した状態でコードセルの途中で終了させたい場合はDeno.exitの代わりに`jupyterExit()`を利用してください。
Deno.exitで終了するとJupyterのユーザー変数は更新されません。

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
