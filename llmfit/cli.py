"""
cli.py - CLI命令处理模块

使用argparse处理命令行参数，提供detect/list/recommend/compare/info等子命令。
"""

import argparse
import sys
from typing import List, Optional

from .database import ModelDatabase
from .detector import detect_all
from .formatter import Formatter
from .scorer import Scorer
from .utils import check_python_version


def _add_global_args(sub_parser: argparse.ArgumentParser) -> None:
    """为子命令添加全局参数（--no-color, --format）"""
    sub_parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="禁用彩色终端输出",
    )
    sub_parser.add_argument(
        "--format", "-f",
        choices=["table", "json", "markdown"],
        default="table",
        help="输出格式 (默认: table)",
    )


def create_parser() -> argparse.ArgumentParser:
    """
    创建CLI参数解析器。

    Returns:
        配置好的ArgumentParser实例
    """
    parser = argparse.ArgumentParser(
        prog="llmfit",
        description="LLMFit - 轻量级本地LLM硬件适配与智能推荐引擎",
        epilog="示例:\n"
               "  llmfit                    # 显示硬件信息 + 推荐最佳模型\n"
               "  llmfit detect             # 仅检测硬件\n"
               "  llmfit list               # 列出所有支持的模型\n"
               "  llmfit recommend --top 5  # 推荐前5个\n"
               "  llmfit recommend --tag coding --format json\n"
               "  llmfit compare \"Llama 3.1 8B\" \"Qwen 2.5 7B\"\n"
               "  llmfit info \"Llama 3.1 8B\"",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"%(prog)s 1.0.0",
    )

    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="禁用彩色终端输出",
    )

    parser.add_argument(
        "--format", "-f",
        choices=["table", "json", "markdown"],
        default="table",
        help="输出格式 (默认: table)",
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # detect 子命令
    detect_parser = subparsers.add_parser(
        "detect",
        help="检测硬件信息",
        description="检测并显示当前系统的硬件配置信息",
    )
    _add_global_args(detect_parser)

    # list 子命令
    list_parser = subparsers.add_parser(
        "list",
        help="列出所有支持的模型",
        description="列出数据库中所有支持的LLM模型",
    )
    _add_global_args(list_parser)
    list_parser.add_argument(
        "--family",
        type=str,
        default=None,
        help="按模型系列过滤",
    )

    # recommend 子命令
    rec_parser = subparsers.add_parser(
        "recommend",
        help="推荐适合的模型",
        description="根据硬件配置推荐最适合的LLM模型",
    )
    _add_global_args(rec_parser)
    rec_parser.add_argument(
        "--top", "-n",
        type=int,
        default=10,
        help="推荐数量 (默认: 10)",
    )
    rec_parser.add_argument(
        "--tag", "-t",
        type=str,
        action="append",
        default=None,
        help="按标签过滤 (可多次使用)",
    )
    rec_parser.add_argument(
        "--min-params",
        type=float,
        default=None,
        help="最小参数量(十亿)",
    )
    rec_parser.add_argument(
        "--max-params",
        type=float,
        default=None,
        help="最大参数量(十亿)",
    )
    rec_parser.add_argument(
        "--min-context",
        type=int,
        default=None,
        help="最小上下文长度",
    )

    # compare 子命令
    cmp_parser = subparsers.add_parser(
        "compare",
        help="对比两个模型",
        description="对比两个模型在当前硬件上的适配情况",
    )
    _add_global_args(cmp_parser)
    cmp_parser.add_argument(
        "model1",
        type=str,
        help="第一个模型名称",
    )
    cmp_parser.add_argument(
        "model2",
        type=str,
        help="第二个模型名称",
    )

    # info 子命令
    info_parser = subparsers.add_parser(
        "info",
        help="查看模型详情",
        description="查看指定模型的详细信息",
    )
    _add_global_args(info_parser)
    info_parser.add_argument(
        "model_name",
        type=str,
        help="模型名称",
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """
    CLI主入口函数。

    Args:
        argv: 命令行参数列表，默认使用sys.argv

    Returns:
        退出码 (0=成功, 1=错误)
    """
    # 检查Python版本
    if not check_python_version((3, 8)):
        print("错误: LLMFit 需要 Python 3.8 或更高版本", file=sys.stderr)
        return 1

    parser = create_parser()
    args = parser.parse_args(argv)

    # 确定输出格式
    output_format = getattr(args, "format", "table")
    use_color = not getattr(args, "no_color", False)

    # 初始化组件
    formatter = Formatter(use_color=use_color)
    database = ModelDatabase()

    # 无子命令时，显示硬件信息 + 推荐
    if args.command is None:
        return _cmd_default(formatter, database, output_format)

    # 分发子命令
    command_map = {
        "detect": _cmd_detect,
        "list": _cmd_list,
        "recommend": _cmd_recommend,
        "compare": _cmd_compare,
        "info": _cmd_info,
    }

    handler = command_map.get(args.command)
    if handler is None:
        parser.print_help()
        return 1

    try:
        return handler(args, formatter, database, output_format)
    except KeyboardInterrupt:
        print("\n操作已取消", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def _cmd_default(
    formatter: Formatter,
    database: ModelDatabase,
    output_format: str,
) -> int:
    """
    默认命令：显示硬件信息 + 推荐最佳模型。

    Args:
        formatter: 格式化器
        database: 模型数据库
        output_format: 输出格式

    Returns:
        退出码
    """
    # 检测硬件
    hardware = detect_all()
    print(formatter.format_hardware(hardware, output_format))
    print("")

    # 推荐模型
    scorer = Scorer(hardware, database)
    recommendations = scorer.recommend(top_n=5)
    print(formatter.format_recommendations(recommendations, output_format))

    return 0


def _cmd_detect(
    args: argparse.Namespace,
    formatter: Formatter,
    database: ModelDatabase,
    output_format: str,
) -> int:
    """
    检测硬件信息。

    Args:
        args: 命令行参数
        formatter: 格式化器
        database: 模型数据库
        output_format: 输出格式

    Returns:
        退出码
    """
    hardware = detect_all()
    print(formatter.format_hardware(hardware, output_format))
    return 0


def _cmd_list(
    args: argparse.Namespace,
    formatter: Formatter,
    database: ModelDatabase,
    output_format: str,
) -> int:
    """
    列出所有支持的模型。

    Args:
        args: 命令行参数
        formatter: 格式化器
        database: 模型数据库
        output_format: 输出格式

    Returns:
        退出码
    """
    family = getattr(args, "family", None)
    models = database.filter_models(family=family)
    print(formatter.format_model_list(models, output_format))
    return 0


def _cmd_recommend(
    args: argparse.Namespace,
    formatter: Formatter,
    database: ModelDatabase,
    output_format: str,
) -> int:
    """
    推荐模型。

    Args:
        args: 命令行参数
        formatter: 格式化器
        database: 模型数据库
        output_format: 输出格式

    Returns:
        退出码
    """
    hardware = detect_all()
    scorer = Scorer(hardware, database)

    recommendations = scorer.recommend(
        top_n=args.top,
        min_params=args.min_params,
        max_params=args.max_params,
        tags=args.tag,
        min_context=args.min_context,
    )

    print(formatter.format_recommendations(recommendations, output_format))
    return 0


def _cmd_compare(
    args: argparse.Namespace,
    formatter: Formatter,
    database: ModelDatabase,
    output_format: str,
) -> int:
    """
    对比两个模型。

    Args:
        args: 命令行参数
        formatter: 格式化器
        database: 模型数据库
        output_format: 输出格式

    Returns:
        退出码
    """
    hardware = detect_all()
    scorer = Scorer(hardware, database)

    result = scorer.compare_models(args.model1, args.model2)
    if result is None:
        model1 = database.get_model(args.model1)
        model2 = database.get_model(args.model2)
        if model1 is None:
            print(f"错误: 未找到模型 '{args.model1}'", file=sys.stderr)
        if model2 is None:
            print(f"错误: 未找到模型 '{args.model2}'", file=sys.stderr)
        return 1

    rec1, rec2 = result
    print(formatter.format_comparison(rec1, rec2, output_format))
    return 0


def _cmd_info(
    args: argparse.Namespace,
    formatter: Formatter,
    database: ModelDatabase,
    output_format: str,
) -> int:
    """
    查看模型详情。

    Args:
        args: 命令行参数
        formatter: 格式化器
        database: 模型数据库
        output_format: 输出格式

    Returns:
        退出码
    """
    model = database.get_model(args.model_name)
    if model is None:
        print(f"错误: 未找到模型 '{args.model_name}'", file=sys.stderr)
        print(f"提示: 使用 'llmfit list' 查看所有支持的模型", file=sys.stderr)
        return 1

    print(formatter.format_model_detail(model, output_format))
    return 0
