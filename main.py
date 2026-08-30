import argparse
import logging
import sys
from pathlib import Path

from config import settings
from src.formatter import console_text
from src.pipeline import ExtractionPipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Word 文档重要事项智能提取系统")
    parser.add_argument("document", type=Path, help="待分析的 .docx 文件")
    parser.add_argument("--output-dir", type=Path, default=settings.OUTPUT_DIR)
    parser.add_argument("--offline", action="store_true", help="只用本地缓存；不可用时启用规则降级")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    try:
        result = ExtractionPipeline(allow_download=not args.offline).run(args.document, args.output_dir)
        print(console_text(result))
        print(f"\nJSON：{result['output_paths']['json']}\nMarkdown：{result['output_paths']['markdown']}")
        return 0
    except (FileNotFoundError, ValueError) as exc:
        logging.error("处理失败：%s", exc)
    except Exception as exc:
        logging.exception("发生未预期错误：%s", exc)
    return 1


if __name__ == "__main__":
    sys.exit(main())

