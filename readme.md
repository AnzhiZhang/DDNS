# DDNS

> 阿里云动态域名解析工具

## 使用

### 安装依赖

```text
pip install -r requirements.txt
```

### 启动

```text
python main.py
```

## 配置

### AccessKeyID

阿里云 AccessKeyID

### AccessKeySecret

阿里云 AccessKeySecret

### Domain

域名

### Records

主机记录名称与类型

参考以下格式：

```json
{
  "RR": "www",
  "Type": "A"
}
```
