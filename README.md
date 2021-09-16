# SiyuanYuque

Sync SiYuanNote & Yuque.

## Install

Use pip to install.

```bash
pip install SiyuanYuque
```

Execute like this:

```bash
python -m SiyuanYuque
```

Remember to create a `sqconfig.toml` config file in the current directory.

```ini
user_token = ""
siyuan_token = ""
api_host = "https://www.yuque.com/api/v2"
last_sync_time = "20210915225457"
```

Fill in your Yuque user_token and siyuan_token.

![image](https://user-images.githubusercontent.com/41664195/133458286-41abaf7a-aab2-4c98-a758-e29f7512a8f6.png)

![image](https://user-images.githubusercontent.com/41664195/133458339-69a698d8-a133-4ef8-9419-ccec7354ddc7.png)

## Set Atrribute in SiyuanNote

You can only sync documents to Yuque.

Set Attributes like this:

![image](https://user-images.githubusercontent.com/41664195/133459061-737ca0ec-aa47-4294-b5db-4b6bb8d6a02d.png)

```ini
yuque: true
yuque-workspace: your workspace
```

Workspace format: `username/repo`

Then run `python -m SiyuanYuque`, and check the attributes again.

![image](https://user-images.githubusercontent.com/41664195/133459218-8bc181aa-2429-4075-b8b3-2b9af4f6ca7f.png)

You'll see `yuque-id` appended to your document's attributes. **Don't manually modify this unless you know what you are doing.**

That's the basic usage for the time being.

**Remember not to edit the documents sync from SiYuan, as the update will be lost upon the next sync.**

## Custom Sync

It is supported to sync documents by SQL.

A simple example:

```toml
user_token = ""
siyuan_token = ""
api_host = "https://www.yuque.com/api/v2"
last_sync_time = "20210916223903"
[[custom_sync]]
sql = "select * from blocks where hpath like '%Math/%' and type='d'"
yuque-workspace = "clouder0/gaokao"
``` 

Multiple custom syncs can be defined.

```toml
user_token = ""
siyuan_token = ""
api_host = "https://www.yuque.com/api/v2"
last_sync_time = "20210916223903"
[[custom_sync]]
sql = "select * from blocks where hpath like '%Math/%' and type='d'"
yuque-workspace = "clouder0/gaokao"
[[custom_sync]]
sql = "select * from blocks where hpath like '%Chinese/%' and type='d'"
yuque-workspace = "clouder0/gaokao"
```
