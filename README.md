# training_queue

深度学习排队训练框架
- 通过 Redis 存储任务进程数据, 方便利用相关客户端远程查看
- 将任务分化为三种状态(运行中, 等待中, 完成), 方便任务管理
- 通过给定的 `min_free_memory` ,设置当前训练任务的预估显存占用大小


## 安装 Redis

### 源码编译

```bash
cd /home/user/program
wget https://download.redis.io/redis-stable.tar.gz
tar -xzvf redis-stable.tar.gz
cd redis-stable
make -j64
cd ./src
make install PREFIX=/home/user/program/redis-7.0
make install -j64  PREFIX=/home/user/program/redis-7.0

```

### 配置本地参数文件

```bash

mv ./redis.conf /home/user/program/redis-7.0/bin
```

修改 `redis.conf` 文件

> 将第 87 行左右的 `bind 127.0.0.1 -::1` 注释掉, 取消与本地 ip 的强制绑定, 方便使用其他电脑远程连接此数据库

> 将第 111 行左右的 `protected-mode yes` 修改为 `protected-mode no` , 取消保护模式, 使得其他电脑远程可以连接此数据库

> 将第 309 行左右的 `daemonize no` 修改为 `daemonize yes` , 打开守护进程, 使得服务端可以独立于控制终端运行(在后台运行)

> 将 871 行左右的 `user worker +@list +@connection ~jobs:* on >ffa9203c493aa99` 附近, 添加一个 `user trainer on +@all -DEBUG ~* >Sudadenglu` , 为训练过程设置一个用户 , 账户名为 `trainer` , 登录密码为 `Sudadenglu` , 拥有读取和写入数据的权限.

> 将 871 行左右的 `user worker +@list +@connection ~jobs:* on >ffa9203c493aa99` 附近, 添加一个 `user default on +@read -DEBUG ~* nopass` , 为数据库设置一个默认用户, 不需要账号密码就能登录, 但是仅有读取的权限, 方便更安全和方便的为远程端服务.

### 运行 Redis 服务器

```bash
/home/user4/program/redis-7.0/bin/redis-server /home/user4/program/redis-7.0/bin/redis.conf
```

## 安装所需 Python 库

```bash
# 安装 Redis 的 Python Api 接口
pip install redis==4.1.0 
# 安装 显卡监控库
pip install nvitop==0.9.0
```

## 将运行代码嵌入等待框架


### 下载此存储库

### 使用此框架(示例如下)
```python
from utils import RedisClient
import time

def train_worker():
    ...
    
if __name__ == '__main__':
    # 初始化并连接到 Redis 服务端
    redis_client = RedisClient(host='127.0.0.1', port=6379, min_free_memory="20GiB", password="?", username="trainer")
    redis_client.check_data()
    redis_client.join_wait_queue()    # 注册当前任务进程到等待任务列表
    while True:
        redis_client.check_data()
        if not redis_client.pop_wait_queue():
            time.sleep(60)    # 休息一下, 再重新尝试
            continue
        if not redis_client.is_can_run():
            time.sleep(60)    # 休息一下, 再重新尝试
            continue
        try:
            # 定义训练主程序
            train_worker(...)
            redis_client.pop_run_queue(success=True)
            break
        except RuntimeError as e:
            if "CUDA out of memory" in e.args[0]:
                redis_client.pop_run_queue(success=False)
                time.sleep(60)
            else:
                raise e
```

cite:

https://zhuanlan.zhihu.com/p/552627015
https://zhuanlan.zhihu.com/p/552967858
https://github.com/D-Yifan/dg_gpu_queuer

