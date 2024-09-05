import os
import czsc
import glob
import pandas as pd

# 投研共享数据的本地缓存路径，需要根据实际情况修改
cache_path = r"D:\CZSC投研数据"


def get_symbols(name, **kwargs):
    """获取指定分组下的所有标的代码

    :param name: 分组名称，可选值：'A股主要指数', 'A股场内基金', '中证500成分股', '期货主力'
    :param kwargs:
    :return:
    """
    files = glob.glob(os.path.join(cache_path, name, "*.parquet"))
    return [os.path.basename(x).replace('.parquet', '') for x in files]


def get_raw_bars(symbol, freq, sdt, edt, fq='前复权', **kwargs):
    """获取 CZSC 库定义的标准 RawBar 对象列表

    :param symbol: 标的代码
    :param freq: 周期，支持 Freq 对象，或者字符串，如
            '1分钟', '5分钟', '15分钟', '30分钟', '60分钟', '日线', '周线', '月线', '季线', '年线'
    :param sdt: 开始时间
    :param edt: 结束时间
    :param fq: 除权类型，投研共享数据默认都是后复权，不需要再处理
    :param kwargs:
    :return:
    """
    kwargs['fq'] = fq
    file = glob.glob(os.path.join(cache_path, "*", f"{symbol}.parquet"))[0]
    freq = czsc.Freq(freq)
    
    kline = pd.read_parquet(file)
    if 'dt' not in kline.columns:
        kline['dt'] = pd.to_datetime(kline['datetime'])
        
    kline = kline[(kline['dt'] >= sdt) & (kline['dt'] <= edt)]  # todo: 需要考虑是否需要对日线数据
    _bars = czsc.resample_bars(kline, freq, raw_bars=True)
    return _bars


bar = get_raw_bars('SZSE.000958', '1分钟', '20210101', '20220101')
# bar = get_raw_bars('000001.SH', '1分钟', '20210101', '20210105')
print(bar)

