
import sys
from pathlib import Path

# Support import from project root
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)
from src.parser.parser import Parser
from src.parse_strategy.alipay_parse_strategy import AlipayParseStrategy
from src.parse_strategy.hsbc_parse_strategy import HsbcParseStrategy
from src.parse_strategy.wechat_parse_strategy import WechatParseStrategy, WechatRawParseStrategy
from src.utils.logger import logger


def main():
    print("Welcome to cash flow tracker tool!")

    # 1. parse files to intended output
    for strategy in [AlipayParseStrategy, WechatParseStrategy, HsbcParseStrategy,
                     WechatRawParseStrategy]:
        parser = Parser(strategy)
        parser.execute()

    # 2. Combine monthly files of all accounts

    # 3. Generate yearly file


if __name__ == "__main__":
    main()
