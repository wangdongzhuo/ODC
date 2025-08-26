import argparse
import os


def validate_paths(input_path, output_path):
    """路径验证函数"""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"已创建输出目录: {output_dir}")


def convert_asc_to_txt(input_path, output_path, input_encoding='utf-8', output_encoding='utf-8'):
    """增强版转换函数"""
    try:
        # 验证路径
        validate_paths(input_path, output_path)

        # 文件行数计数器
        line_count = 0

        with open(input_path, 'r', encoding=input_encoding) as asc_file:
            with open(output_path, 'w', encoding=output_encoding) as txt_file:
                for line in asc_file:
                    txt_file.write(line)
                    line_count += 1

                print(f"\n转换完成: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
                print(f"输入文件路径: {os.path.abspath(input_path)}")
                print(f"输出文件路径: {os.path.abspath(output_path)}")
                print(f"总转换行数: {line_count:,}")

    except Exception as e:
        print(f"\n错误发生: {str(e)}")
        if isinstance(e, UnicodeDecodeError):
            print("建议尝试使用以下编码：")
            print("- gbk/gb2312 (简体中文)")
            print("- big5 (繁体中文)")
            print("- latin-1 (西欧语言)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="asc2txt",
        description="ASC 到 TXT 转换器 (支持自定义路径)",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('input',
                        default= "/home/songyuant/PycharmProjects/ODCSOFTbackup/ODCSOFT/monitorODC/ODC_data/data-original/金龙L2测试采集数据/2025-03-05_16点03分_ACC刹不停溜车.asc",
                        help="输入文件路径 (支持相对/绝对路径)\n示例: C:\\data\\input.asc 或 ../source/test.asc")

    parser.add_argument('output',
                        default= "/home/songyuant/PycharmProjects/ODCSOFTbackup/ODCSOFT/monitorODC/ODC_data/data-original/change2txt",
                        help="输出文件路径 (自动创建目录)\n示例: /output/results.txt 或 ./converted/data.txt")

    parser.add_argument('--input_enc',
                        default='utf-8',
                        help="输入文件编码 (默认: utf-8)\n常用值: gbk, big5, latin-1")

    parser.add_argument('--output_enc',
                        default='utf-8',
                        help="输出文件编码 (默认: utf-8)\n常用值: utf-8-sig, gb18030")

    args = parser.parse_args()

    convert_asc_to_txt(
        args.input,
        args.output,
        args.input_enc,
        args.output_enc
    )