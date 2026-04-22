import os

# 【改成你自己的文件夹路径】
folder_path = r"D:\python_atmosphere\mesoscale_homework\wrf_data\index_1"

# 遍历文件夹里所有文件
for filename in os.listdir(folder_path):
    # 只处理 以 wrfout 开头 的文件（WRF原始输出）
    if filename.startswith("wrfout"):
        # 去掉原来的后缀，统一加上 .nc
        new_filename = os.path.splitext(filename)[0] + ".nc"
        
        old_path = os.path.join(folder_path, filename)
        new_path = os.path.join(folder_path, new_filename)
        
        # 重命名
        os.rename(old_path, new_path)
        print(f"✅ 已修改：{filename}  →  {new_filename}")

print("\n🎉 全部 WRF 文件已批量改为 .nc 后缀！")