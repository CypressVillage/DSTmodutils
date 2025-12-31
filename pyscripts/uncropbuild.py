import json
import os
from PIL import Image
import sys
from PIL import Image

def paste(dst_img, src_img, box):
    """
    纯 PIL 实现的精确粘贴（无 numpy），保证像素值不变。
    原理：分别 paste R/G/B/A 四个单通道图像（单通道 paste 是直接赋值，无 blend）。
    """
    if dst_img.mode != "RGBA":
        raise ValueError("dst_img must be in 'RGBA' mode")
    
    src = src_img.convert("RGBA")
    x, y = box
    
    # 分离通道
    r, g, b, a = src.split()
    channels = [r, g, b, a]
    
    # 提取 dst 的四个通道（注意：split() 返回 tuple，需转 list 才能修改）
    dr, dg, db, da = dst_img.split()
    dst_channels = [dr.copy(), dg.copy(), db.copy(), da.copy()]  # 必须 copy！否则只读
    
    # 分别粘贴每个单通道（单通道 paste 不会 blend，是直接覆盖）
    for i, ch in enumerate(channels):
        dst_channels[i].paste(ch, box)
    
    # 合并并写回
    result = Image.merge("RGBA", dst_channels)
    dst_img.paste(result)
def process_json_and_images(json_path):
    # 读取 JSON 文件
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    base_dir = os.path.dirname(json_path)

    if "Symbol" not in data:
        print("JSON 中没有 'Symbol' 字段。")
        return

    symbol = data["Symbol"]

    for part_name, frames in symbol.items():
        print(f"处理部件: {part_name}")
        for frame in frames:
            framenum = frame["framenum"]
            x = -frame["x"]
            y = -frame["y"]
            w = frame["w"]
            h = frame["h"]

            # 构建图片路径: {part_name}/{part_name}-{framenum}.png
            img_filename = f"{part_name}-{framenum}.png"
            img_dir = os.path.join(base_dir, part_name)
            img_path = os.path.join(img_dir, img_filename)

            if not os.path.exists(img_path):
                print(f"警告: 图片不存在，跳过 {img_path}")
                continue

            # 计算新尺寸
            new_w = int(w + 2 * abs(x))
            new_h = int(h + 2 * abs(y))

            # 打开原图（确保有 alpha 通道）
            with Image.open(img_path) as img:
                img = img.convert("RGBA")

                # 创建透明新画布
                new_img = Image.new("RGBA", (new_w, new_h), (0,0,0, 0))

                # 原图中要对齐到新画布中心的点（注意：PIL 坐标是 (x, y)，即 (宽方向, 高方向)）
                # 原图中的参考点：(w/2 + x, h/2 + y) —— 注意：x 是水平偏移，y 是垂直偏移
                # 但在图像坐标系中，x 对应 width（列），y 对应 height（行）
                src_center_x = w / 2 + x   # 水平方向
                src_center_y = h / 2 + y   # 垂直方向

                dst_center_x = new_w / 2
                dst_center_y = new_h / 2

                # 计算粘贴时左上角的偏移
                paste_x = int(dst_center_x - src_center_x)
                paste_y = int(dst_center_y - src_center_y)

                # 粘贴原图到新画布
                paste(new_img,img, (paste_x, paste_y))

                # 保存覆盖原图
                new_img.save(img_path)
                print(f"  已处理并覆盖: {img_path}")

            # 更新 JSON 中的字段
            frame["w"] = new_w
            frame["h"] = new_h
            frame["x"] = 0
            frame["y"] = 0

    # 写回修改后的 JSON（覆盖原文件）
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"✅ 所有处理完成，JSON 已更新: {json_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python script.py <json_file_path>")
        sys.exit(1)

    json_file = sys.argv[1]
    if not os.path.isfile(json_file):
        print(f"错误: 文件不存在 {json_file}")
        sys.exit(1)

    process_json_and_images(json_file)