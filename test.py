from utils import RedisClient
import time

def train_worker():
    ...
    
if __name__ == '__main__':
    # 初始化并连接到 Redis 服务端
    redis_client = RedisClient(host='127.0.0.1', port=6379, min_free_memory="20GiB", password="yoursmassward", username="trainer")
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
