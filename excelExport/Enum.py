# -*- coding: utf-8 -*-
from enum import Enum
from enum import unique


@unique
class ValueType(Enum):
    Null = 0     # 不导出

    KeyNumber = "KeyNumber"		# 数字 key
    Number = "Number"			# 数字 默认:0
    NumberOrNull = "NumberOrNull"  # 数字 默认不导出
    NumberArrays = "[Num，*]"			# 数字数组，[1,2]
    NumberMultiArrays = "[[Num，*]]"		# 数字数组，[[1,2],[3,4]]

    Enum = "Enum"				# 枚举类型，英文 如果填写，自动生成枚举文件

    KeyString = "KeyString"		# 字符串 key
    String = "String"			# 字符串 默认：""
    StringOrNull = "StringOrNull"  # 字符串 默认不导出
    StringArrays = "[String，*]"		# 字符串数组，["a","b"]

    # Native          	= "Native"			# 原样导出


@unique
class OutputType(Enum):
    All = 0   # 导出全部
    Client = 1   # 只导出客户端
    Server = 2   # 只导出服务端
