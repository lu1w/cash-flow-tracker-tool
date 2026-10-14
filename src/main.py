
import sys
from pathlib import Path

if __name__ == "__main__":
    # Support import from project root
    project_root = str(Path(__file__).parent.parent)
    sys.path.append(project_root)

from src.categorizer.categorizer import Categorizer
from src.combiner.combiner import merge_by_month
from src.parser.parser import Preparser, Parser
from src.parse_strategy.alipay_parse_strategy import AlipayParseStrategy
# from src.parse_strategy.hsbc_parse_strategy import HsbcParseStrategy
from src.parse_strategy.wechat_parse_strategy import WechatPreparseStrategy, WechatParseStrategy  # , WechatRawParseStrategy
from src.parse_strategy.wechat_parse_strategy_v1 import WechatRawParseStrategy  # TODO: move this to a pre-parse strategy
from src.utils.logger import logger


def main():
    print("Welcome to cashflow tracker tool!")

    # 1. preparse file if needed
    for strategy in [
        # WechatPreparseStrategy,
    ]:
        preparser = Preparser(strategy)
        preparser.execute()

    # 2. parse files
    for strategy in [
        # AlipayParseStrategy,
        WechatParseStrategy,
        # HsbcParseStrategy,
        # WechatRawParseStrategy
    ]:
        parser = Parser(strategy)
        parser.execute()

    exit()

    categorizer = Categorizer()
    from src.enum.account import Account
    accounts_for_testing = (Account.ALIPAY,)
    categorizer.process_all_standardized_files()

    # 3. Combine monthly files of all accounts
    merge_by_month()

    # 4. Generate yearly file


if __name__ == "__main__":
    main()
