import numpy as np
from collections import OrderedDict
from czsc.analyze import CZSC, Direction
from czsc.signals.tas import update_macd_cache
from czsc.utils import create_single_signal


def tas_test(c: CZSC, **kwargs) -> OrderedDict:
    """DIFF 远离零轴后靠近零轴，形成买卖点

    参数模板："{freq}_DIF靠近零轴T{t}_BS辅助V240612"

    **信号逻辑：**

    买点的定位以DIF为主，要求如下。
    1，取最近一个向下笔的底分型中的DIFF的最小值
    2. 如果这个最小值在零轴的一个0.5倍标准差范围，那么就认为这个最小值是一个有效的买点

    飞书文档：https://s0cqcxuy3p.feishu.cn/wiki/R9Y5w1w3Qi1jsHkzSyLcjoVWnld

    **信号列表：**

    - Signal('60分钟_DIF靠近零轴T50_BS辅助V240612_买点_任意_任意_0')
    - Signal('60分钟_DIF靠近零轴T50_BS辅助V240612_卖点_任意_任意_0')

    :param c: CZSC对象
    :param kwargs: 无

        - t: DIF波动率的倍数，除以100，默认为50

    :return: 信号识别结果
    """
    t = int(kwargs.get("t", 50))  # 波动率的倍数，除以100

    freq = c.freq.value
    k1, k2, k3 = f"{freq}_DIF靠近零轴T{t}_BS辅助V240612".split("_")
    v1 = "其他"
    key = update_macd_cache(c)
    # for item in c.bi_list:
    #     print(item)

    if len(c.bars_raw) < 110 or len(c.bars_ubi) > 7:
        return create_single_signal(k1=k1, k2=k2, k3=k3, v1=v1)

    bi = c.bi_list[-1]
    if len(bi.raw_bars) < 7:
        return create_single_signal(k1=k1, k2=k2, k3=k3, v1=v1)

    diffs = [x.cache[key]["dif"] for x in bi.raw_bars]
    delta = np.std(diffs) * t / 100
    max_diff = max(diffs)
    min_diff = min(diffs)
    abs_mean_diff = abs(np.mean(diffs))
    std_diff = np.std(diffs)

    if bi.direction == Direction.Down and delta > diffs[-1] > -delta and max_diff > abs_mean_diff + std_diff:
        v1 = "买点"

    if bi.direction == Direction.Up and -delta < diffs[-1] < delta and min_diff < -(abs_mean_diff + std_diff):
        v1 = "卖点"

    return create_single_signal(k1=k1, k2=k2, k3=k3, v1=v1)


def check():
    from czsc.connectors import research
    from czsc.traders.base import check_signals_acc

    symbols = research.get_symbols("自选股")
    bars = research.get_raw_bars(symbols[0], "5分钟", "20240101", "20240901", fq="前复权")

    signals_config = [{"name": tas_test, "freq": "30分钟", "t": 50}]
    check_signals_acc(bars, signals_config=signals_config, height="1360px", delta_days=5)  # type: ignore


if __name__ == "__main__":
    check()
