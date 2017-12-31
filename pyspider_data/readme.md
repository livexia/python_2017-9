### 利用pyspider爬取v2ex，并保存到mongodb


my_result_worker.py：重写Worker，使得爬取结果保存在mongodb中

v2ex_pyspider.py：pyspider脚本

config.json：重写worker需要在启动时修改默认配置文件，我这里就是添加了worker的路径。
```json
{
    ……
    "result_worker": {
        "result_cls": "my_result_worker.MyResultWorker"
    },
    ……
}
```