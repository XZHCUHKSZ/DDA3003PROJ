"""
命令行入口。

使用方式:
    python main.py                            # 使用默认路径
    python main.py --data path/to/data.csv    # 指定数据文件
    python main.py --data data.csv --out visualizations/
"""

from __future__ import annotations

import argparse
import os

from visualizer import InteractiveAirQualityMap


def _parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description='中国城市空气质量地图可视化工具（滚动布局版）',
    )
    parser.add_argument(
        '--data',
        default=r'C:\Users\xzh88\Desktop\cleaned\combined_air_quality_data.csv',
        help='输入 CSV 数据文件路径',
    )
    parser.add_argument(
        '--out',
        default=r'C:\Users\xzh88\Desktop\cleaned\visualizations',
        help='输出目录路径（不存在时自动创建）',
    )
    return parser.parse_args()


def main() -> None:
    """程序主入口：解析参数、加载数据、生成可视化输出。"""
    args = _parse_args()

    if not os.path.exists(args.data):
        print(f"\n❌ 找不到数据文件: {args.data}")
        return

    visualizer = InteractiveAirQualityMap(args.data)
    visualizer.load_data()
    visualizer.run(output_dir=args.out)
    print("\n✅ 程序执行完成！")


if __name__ == '__main__':
    main()
    input("\n按回车键退出...")
