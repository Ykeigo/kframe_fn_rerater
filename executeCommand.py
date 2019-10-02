import subprocess

# コマンド実行して結果を文字列でもらう
def res_cmd_lfeed(cmd):
    return subprocess.Popen(
        cmd, stdout=subprocess.PIPE,
        shell=True).stdout.readlines()


# 実行結果文字列をutf8にして¥n消す
def res_cmd(cmd):
    res = res_cmd_lfeed(cmd)
    for i in range(len(res)):
        res[i] = res[i].decode("utf-8")
    return [str(x).replace("\n", "") for x in res]
