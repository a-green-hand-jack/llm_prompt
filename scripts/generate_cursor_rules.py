"""
本脚本用于自动化地将 `模版/` 目录下的 Markdown 规范文件
转换为 Cursor AI 助手可以识别的 `.mdc` 规则文件。

功能：
1. 遍历 `模版/` 目录，查找所有 `.md` 文件。
2. 根据文件名和预设规则，判断每个规范文件是否需要“总是应用” (`alwaysApply`)。
3. 为每个 Markdown 文件生成一个对应的 `.mdc` 文件。
4. 在每个 `.mdc` 文件的顶部插入一个 YAML Front Matter，其中包含元数据。
5. 将生成的所有 `.mdc` 文件保存到项目根目录下的 `.cursor/rules/` 目录中。
"""

import logging
import os
from pathlib import Path

# --- 项目路径定义 ---
# 使用 Path(__file__) 来确保无论从哪里运行脚本，路径都是正确的
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
TEMPLATES_DIR: Path = PROJECT_ROOT / "模版"
OUTPUT_DIR: Path = PROJECT_ROOT / ".cursor" / "rules"

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def _get_globs_for_file(file_path: Path) -> list[str]:
    """
    根据文件名和内容（待实现）为规则文件生成合适的 globs 模式。

    Args:
        file_path (Path): Markdown 文件的路径。

    Returns:
        list[str]: 一个包含 glob 模式的列表。
    """
    name = file_path.name
    content = file_path.read_text(encoding="utf-8").lower()

    if "Python编码规范" in name or "py " in name.lower() or ".py" in content:
        return ["**/*.py", "**/pyproject.toml"]
    if "Git工作流规范" in name:
        return ["**/*"]  # Git 规范适用于所有文件
    if "测试策略与规范" in name:
        return ["**/tests/**/*.py", "**/*_test.py"]
    if "项目初始化模版" in name or "项目结构" in name:
        return ["**/pyproject.toml", "**/README.md"]

    # 默认情况下，模板文件适用于所有 markdown 文件
    return ["**/*.md"]


def _should_always_apply(file_path: Path) -> bool:
    """
    根据文件名判断规则是否应始终应用。

    这是一个基于启发式规则的简单分类器。
    - "编码规范"、"项目结构" 这类基础性强的规范，通常需要一直遵守。
    - 其他的 "模板" 或 "工作流" 更可能是在特定任务时才需要参考。

    Args:
        file_path (Path): Markdown 文件的路径。

    Returns:
        bool: 如果规则应始终应用，则返回 True，否则返回 False。
    """
    always_apply_keywords = ["Python编码规范", "py 项目结构模版"]
    return any(keyword in file_path.name for keyword in always_apply_keywords)


def create_mdc_rule_file(md_file_path: Path, output_dir: Path) -> None:
    """
    根据给定的 Markdown 文件创建一个 Cursor `.mdc` 规则文件。

    Args:
        md_file_path (Path): 原始 Markdown 文件的路径。
        output_dir (Path): `.mdc` 文件将被保存的目标目录。
    """
    try:
        # 1. 读取原始 Markdown 内容
        original_content: str = md_file_path.read_text(encoding="utf-8")

        # 2. 判断规则类型
        always_apply: bool = _should_always_apply(md_file_path)

        # 3. 构建 YAML Front Matter
        # description 暂时留空，可以让用户在 Cursor IDE 中自行填写
        globs_list = _get_globs_for_file(md_file_path)
        globs_str = str(globs_list).replace("'", '"')  # 转为json格式

        yaml_front_matter = f"""---
description: "{md_file_path.stem}"
globs: {globs_str}
alwaysApply: {str(always_apply).lower()}
---

"""
        # 4. 组合成新的 .mdc 文件内容
        mdc_content: str = yaml_front_matter + original_content

        # 5. 定义输出文件路径
        output_filename = md_file_path.with_suffix(".mdc").name
        output_filepath = output_dir / output_filename

        # 6. 写入文件
        output_filepath.write_text(mdc_content, encoding="utf-8")
        logging.info(
            f"  - 已成功创建规则: '{output_filepath.name}' (alwaysApply: {always_apply})"
        )

    except Exception as e:
        logging.error(f"处理文件 {md_file_path.name} 时发生错误: {e}")


def main() -> None:
    """脚本主入口函数。"""
    # 确保输出目录存在
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        logging.info(f"已确保输出目录存在: '{OUTPUT_DIR}'")
    except OSError as e:
        logging.critical(f"创建输出目录失败: {e}")
        return

    # 检查模板目录是否存在
    if not TEMPLATES_DIR.is_dir():
        logging.error(f"模板目录不存在: {TEMPLATES_DIR}")
        return

    logging.info(f"开始从 '{TEMPLATES_DIR}' 目录扫描并转换规则文件...")

    # 遍历并转换所有 Markdown 文件
    md_files = list(TEMPLATES_DIR.glob("*.md"))
    if not md_files:
        logging.warning("在模板目录中没有发现任何 .md 文件。")
        return

    for md_file in md_files:
        create_mdc_rule_file(md_file, OUTPUT_DIR)

    logging.info("所有规则文件已成功转换为 .mdc 格式！")


if __name__ == "__main__":
    main()
