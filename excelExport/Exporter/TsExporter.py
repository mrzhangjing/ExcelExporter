# -*- coding: utf-8 -*-
import os
import re
from Enum import ValueType, OutputType
from Exporter.Exporter import Exporter


class TsExporter(Exporter):
    def __init__(self, fileName="", tableName=""):
        # print('TsParser')
        Exporter.__init__(self, fileName, tableName)
        self.server_path = self.config.get('Ts', 'server_path')
        self.client_path = self.config.get('Ts', 'client_path')

        self.VOName = "_" + self.tableName
        self.VOName = re.sub(r'(_\w)', lambda x: x.group(1)[
                             1].upper(), self.VOName)
        self.VOName = self.VOName.replace('Config', '')
        self.VOName = self.VOName.replace('VO', '')
        self.VOName = self.VOName + "VO"

    def exportOther(self):
        self._exportConfigCache()

    def exportConfig(self, VOParser):
        self.exportTable(VOParser)
        self.exportVO(VOParser)

    def exportTable(self, VOParser):
        TableTmp = self.readTemplet("Table.ts.tmp")

        # 导出Table对象
        ShortName = self.VOName.replace('VO', '')

        TableName = ShortName + 'Table'
        TableTmp = TableTmp.replace("%ShortName%", ShortName)
        TableTmp = TableTmp.replace("%file_name%", self.tableName)

        TableEnum = ""
        for enum in VOParser.enumList:
            tmp = "    enum = code,\n"
            tmp = tmp.replace("enum", enum)
            tmp = tmp.replace("code", str(VOParser.enumList[enum]))
            TableEnum = TableEnum + tmp
        if TableEnum == "":
            TableTmp = TableTmp.replace("\n%TableEnum%", "")
        else:
            TableEnum = "export enum %ShortName%TableEnum {\n" + TableEnum + "}"
            TableEnum = TableEnum.replace("%ShortName%", ShortName)
            TableTmp = TableTmp.replace("%TableEnum%", TableEnum)

        initKey = ""
        findByKey = ""
        if 0 in VOParser.clientTitleIndex and VOParser.clientTitleIndex[0] != None:
            title = VOParser.clientTitleIndex[0]
            if title['valueType'] is ValueType.KeyNumber or title['valueType'] is ValueType.KeyString:
                key = title['key']
                valueType = "number"
                if title['valueType'] is ValueType.KeyString:
                    valueType = "string"
                initKey = "this.VOMap.set(VO.%key%, VO)"
                initKey = initKey.replace("%key%", key)
                # print(initKey)

                findByKey = """
    VOMap: Map<%valueType%, %VOName%> = new Map();
    public findBy%Key%(%key%: %valueType%): %VOName% {
        return this.VOMap.get(%key%)
    }\n"""
                findByKey = findByKey.replace("%VOName%", self.VOName)
                findByKey = findByKey.replace("%Key%", key.capitalize())
                findByKey = findByKey.replace("%key%", key)
                findByKey = findByKey.replace("%valueType%", valueType)

        TableTmp = TableTmp.replace("%initKey%", initKey)
        TableTmp = TableTmp.replace("%findByKey%", findByKey)
        self.writeFile(self.client_path, TableName + '.ts', TableTmp)

    def exportVO(self, VOParser):
        VOTmp = self.readTemplet("VO.ts.tmp")

        VOTmp = VOTmp.replace('%VOName%', self.VOName)
        initMemberCode = ""
        memberCode = ""
        index = 0
        for i in VOParser.clientTitleIndex:
            # valueOutput = VOParser.clientTitleIndex[i]['output']
            # if valueOutput != OutputType.All.name and valueOutput != output:
            #     continue

            initFormat = """
		this.%key% = data[%index%];"""
            initFormat = initFormat.replace(
                "%key%", VOParser.clientTitleIndex[i]['key'])
            initFormat = initFormat.replace("%index%", str(index))
            index = index + 1
            initMemberCode = initMemberCode + initFormat

            memberFormat = """
	// %desc%
	public readonly %key%: %valueType%;"""
            memberFormat = memberFormat.replace(
                "%desc%", VOParser.clientTitleIndex[i]['desc'])
            memberFormat = memberFormat.replace(
                "%key%", VOParser.clientTitleIndex[i]['key'])
            valueType = VOParser.clientTitleIndex[i]['valueType']
            if valueType is ValueType.KeyNumber:
                valueType = "number"
            elif valueType is ValueType.Number:
                valueType = "number"
            elif valueType is ValueType.NumberOrNull:
                valueType = "number | null"
            elif valueType is ValueType.NumberArrays:
                valueType = "number[] | null"
            elif valueType is ValueType.NumberMultiArrays:
                valueType = "number[][] | null"
            elif valueType is ValueType.Enum:
                valueType = "string"
            elif valueType is ValueType.KeyString:
                valueType = "string"
            elif valueType is ValueType.String:
                valueType = "string"
            elif valueType is ValueType.Enum:
                valueType = "string | null"
            elif valueType is ValueType.StringOrNull:
                valueType = "string | null"
            elif valueType is ValueType.StringArrays:
                valueType = "string[] | null"
            else:
                valueType = "string | null"
            memberFormat = memberFormat.replace("%valueType%", valueType)
            memberCode = memberCode + memberFormat

        VOTmp = VOTmp.replace('%initMemberCode%', initMemberCode)
        VOTmp = VOTmp.replace('%memberCode%', memberCode)
        self.writeFile(self.client_path, self.VOName + '.ts', VOTmp)

    # 导出 Tbl.ts
    def _exportConfigCache(self):
        print("生成：> Tbl.ts")
        TblTmp = self.readTemplet("Tbl.ts.tmp")

        importCode = ""
        memberCode = ""
        initMemberCode = ""
        for fileName in os.listdir(self.client_path):
            if '~$' in fileName:
                continue
            if fileName.find("Table.ts") == -1:
                continue
            ShortName = fileName.replace("Table.ts", "")
            importCode = importCode + \
                "import %ShortName%Table from \"./%ShortName%Table\";\n".replace(
                    "%ShortName%", ShortName)
            memberCode = memberCode + \
                "    public static %ShortName%Table: %ShortName%Table = null;\n".replace(
                    "%ShortName%", ShortName)
            initMemberCode = initMemberCode + \
                "        tbl.%ShortName%Table = new %ShortName%Table();\n".replace(
                    "%ShortName%", ShortName)

        TblTmp = TblTmp.replace("%importCode%", importCode)
        TblTmp = TblTmp.replace("%memberCode%", memberCode)
        TblTmp = TblTmp.replace("%initMemberCode%", initMemberCode)
        self.writeFile(self.client_path, 'Tbl.ts', TblTmp)
