import subprocess
import shlex
import base64
import tempfile
import os
import json
import IPython.display as display  # type: ignore
from IPython.core.magic import register_cell_magic  # type: ignore


# Google Colabで実行しているかどうかを判定
def is_google_colab():
    try:
        import google.colab  # type: ignore  # noqa: F401
        return True
    except ImportError:
        return False


# Denoコマンド
def get_deno_cmd():
    if is_google_colab():
        return "/root/.deno/bin/deno"
    else:
        return "deno"


def install_deno_colab():
    """
    Denoのインストール(Google Colab用)
    """
    if not is_google_colab():
        print("Google Colab環境ではありません。Denoのインストールをスキップします。")
        return

    # Denoのインストールコマンド
    command = "curl -fsSL https://deno.land/x/install/install.sh | sh"

    # シェルコマンドを実行
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # 出力を表示
    if process.returncode == 0:
        print("Denoをインストールしました。")
        print(stdout.decode())
    else:
        print("Denoのインストール中にエラーが発生しました。")
        print(stderr.decode())


def register_deno_magics():
    """
    Denoセルマジックコマンドを登録
    """
    from IPython import get_ipython  # type: ignore
    ipy = get_ipython()
    ipy.register_magic_function(run_deno)
    ipy.register_magic_function(run_deno_iframe)
    ipy.register_magic_function(view_deno_iframe)
    ipy.register_magic_function(run_deno_bundle_iframe)
    ipy.register_magic_function(view_deno_bundle_iframe)
    print("Denoセルマジックコマンドを登録しました。")


@register_cell_magic
def run_deno(line, cell):
    """
    Denoのコードを実行するマジックコマンド
    """
    args = shlex.split(line)

    useval = args[0] if len(args) > 0 else "False"

    # Jupyterのユーザー変数を取得してDenoスクリプト内で使用可能にする
    if useval.lower() == "true":
        curdir = os.getcwd()
        curdir = curdir.replace("\\", "/")

        # Jupyterのユーザー変数を取得してJSONファイルに変換し、一時ファイルに保存
        with tempfile.NamedTemporaryFile(dir=curdir, suffix=".json", delete=False) as json_file:
            # IPythonのユーザー名前空間を取得
            from IPython import get_ipython  # type: ignore
            ipython = get_ipython()
            variables = ipython.user_ns

            # シリアライズ可能な変数のみをフィルタリング
            def is_serializable(obj):
                try:
                    json.dumps(obj)
                    return True
                except (TypeError, OverflowError):
                    return False

            filtered_vars = {name: value for name, value in variables.items() if is_serializable(value)}

            # JSON形式に変換
            json_data = json.dumps(filtered_vars)
            json_file.write(json_data.encode("utf-8"))
            json_file_path = json_file.name

            esc_json_file_path = json_file_path.replace("\\", "\\\\")

        # Jupyterのグローバル変数を取得・変更・追加するDenoスクリプト
        pre_script = f"""
globalThis.isJupyterCell = true;
globalThis.jupyter = JSON.parse(Deno.readTextFileSync('{esc_json_file_path}'));
globalThis.jupyterExit = function(code = 0) {{
    Deno.writeTextFileSync('{esc_json_file_path}', JSON.stringify(globalThis.jupyter));
    Deno.exit(code);
}}
        """

        after_script = """
jupyterExit();
        """

    else:
        pre_script = """
globalThis.isJupyterCell = true;
globalThis.jupyterExit = function(code = 0) {
    Deno.exit(code);
}
        """

        after_script = ""

    cell = pre_script + cell + after_script

    # Denoコマンドを実行
    denocmd = get_deno_cmd()
    process = subprocess.Popen(
        [denocmd, "eval", cell],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdout, stderr = process.communicate()

    if useval.lower() == "true":
        # 一時JSONファイルからグローバル変数を復元
        with open(json_file_path, "r") as f:
            # IPythonのユーザー名前空間を取得
            from IPython import get_ipython  # type: ignore
            ipython = get_ipython()
            variables = ipython.user_ns

            external_data = json.load(f)

            # user_nsを更新する
            for key, value in external_data.items():
                variables[key] = value
        os.remove(json_file_path)

    # 結果を表示
    if process.returncode == 0:
        print(stdout.decode("utf-8"))
    else:
        print(stderr.decode("utf-8"))


@register_cell_magic
def run_deno_iframe(line, cell):
    """
    DenoのコードをトランスパイルしてIframeで表示するマジックコマンド
    """
    run_iframe(line, cell, "transpile", False)


@register_cell_magic
def view_deno_iframe(line, cell):
    """
    DenoのコードトランスパイルしてHTMLと一緒に表示するマジックコマンド
    """
    run_iframe(line, cell, "transpile", True)


@register_cell_magic
def run_deno_bundle_iframe(line, cell):
    """
    DenoのコードとライブラリをバンドルしてIframeで表示するマジックコマンド
    """
    run_iframe(line, cell, "bundle", False)


@register_cell_magic
def view_deno_bundle_iframe(line, cell):
    """
    DenoのコードとライブラリをバンドルしたコードとHTMLを表示するマジックコマンド
    """
    run_iframe(line, cell, "bundle", True)


# マジックコマンドの共通処理
def run_iframe(line, cell, type, viewmode):
    args = shlex.split(line)
    width = args[0] if len(args) > 0 else 500
    height = args[1] if len(args) > 1 else 500
    srcs = args[2:] if len(args) > 2 else []

    js_code = deno_transpile(cell, type)

    if js_code is None:
        return

    output_iframe(js_code, width, height, srcs, viewmode)


# Denoのコードをトランスパイル
def deno_transpile(code, type):
    curdir = os.getcwd()

    curdir = curdir.replace("\\", "/")

    with tempfile.NamedTemporaryFile(dir=curdir, suffix=".ts", delete=False) as ts_file:
        ts_file.write(code.encode('utf-8'))
        ts_file_base_path = ts_file.name
        ts_file_path = ts_file_base_path.replace("\\", "/")

    deno_script = f"""
import {{ {type} }} from "https://deno.land/x/emit/mod.ts";

const url = new URL("file://{ts_file_path}", import.meta.url);
const result = await {type}(url.href);

let code = "";
if ("{type}" === "transpile") {{
    code = result.get(url.href);
}} else if ("{type}" === "bundle"){{
    code = result.code;
}}

console.log(code);
    """.strip()

    with tempfile.NamedTemporaryFile(dir=curdir, suffix=".ts", delete=False) as deno_file:
        deno_file.write(deno_script.encode('utf-8'))
        deno_file_path = deno_file.name

    # Denoスクリプトを実行し、出力をキャプチャ
    denocmd = get_deno_cmd()
    process = subprocess.Popen(
        [denocmd, "run", "--allow-all", deno_file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdout, stderr = process.communicate()

    os.remove(ts_file_base_path)
    os.remove(deno_file_path)

    if process.returncode == 0:
        return stdout.decode("utf-8")
    else:
        # エラーが発生した場合のエラーメッセージ
        print("トランスパイル中にエラーが発生しました:")
        print(stderr.decode("utf-8"))
        return None


# IFrameで表示
def output_iframe(js_code, width, height, srcs, viewmode):
    # srcsで指定されたファイル群をScriptタグに変換
    if len(srcs) > 0:
        src_tags = "\n".join([f"""    <script src="{src}"></script>""" for src in srcs])
        src_tags = f"\n{src_tags}"
    else:
        src_tags = ""

    # iframeに表示するHTMLを作成
    base_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">{src_tags}
</head>
<body>
    <div id="error" style="color: red; font-weight: bold; display: none;"></div>
    <script>
        window.addEventListener('error', function(event) {{
            document.getElementById('error').innerHTML = "Error: " + event.message;
            document.getElementById('error').style.display = 'block';
            return false;
        }});
    </script>
    <script type="module">
{js_code}
    </script>
</body>
</html>
    """.strip()

    if viewmode:
        # HTMLを表示
        print(base_html)
    else:
        # HTMLをデータURIとしてエンコード
        data_uri = "data:text/html;base64," + base64.b64encode(base_html.encode("utf-8")).decode("utf-8")

        # IFrameを使用して表示
        display.display(display.IFrame(src=data_uri, width=width, height=height))
