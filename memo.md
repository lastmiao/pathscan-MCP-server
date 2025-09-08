# 学习开发fastmcp中学到的知识

## subprocess.run()
### shell
在shell为False的时候, 命令会直接当作可执行文件来运行
在shell为True的时候, 命令会在shell中执行,于是可以执行shell中的命令,在Windows中为cmd
**例子:**
```python
command  = [
    "dir"
]

subprocess.run(command,shell=False)
#程序对执行失败, 应为dir是cmd内置命令, 在设置shell为False时, 只能执行可执行文件ping
```

## capture_output
capture_output就想到于是开启了导流, 把原本输出到终端中的信息导流到了Python程序中

## capture_output 和 stdout,stderr 的区别

`capture_output=True` | 等价于 `stdout=PIPE, stderr=PIPE`，两种输出都能捕获 
`stdout=PIPE`         | 只捕获标准输出，错误输出还是去终端                   
`stderr=PIPE`         | 只捕获错误输出，标准输出还是去终端                  


## text
默认关闭, 输出为字节串, 开启后输出字符流

## encoding
- text=True 会用系统默认编码（Windows 通常是 gbk，Linux 通常是 utf-8）
- 如果你想强制指定编码，可以用 encoding

## check
- 默认情况下：无论命令是否成功（退出码是不是 0），subprocess.run 都不会报错。
- check=True 时：如果命令的返回码（returncode）不是 0，就会抛出异常 subprocess.CalledProcessError

