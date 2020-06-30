"""
用于html清洗
"""
import re


class HtmlClean(object):

    def __init__(self, html_string):
        self._data = html_string

    def clean(self):
        """
        数据清洗，删除html script/style
        :return:
        """
        # 删除script
        self._data = re.sub(r'<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', '', self._data, flags=re.I)
        # 删除style
        self._data = re.sub(r'<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', '', self._data, flags=re.I)
        # 删除多余的空格及换行符
        self._data = re.sub(r'\s{2,}', '', self._data)
        # 删除无法删除的script
        while self._data.find('<script>') != -1:
            start_index = self._data.find('<script>')
            end_index = self._data.find('</script>')
            if end_index == -1:
                break
            self._data = self._data[:start_index] + self._data[end_index + len('</script>'):]
        # 处理多余的titlelast
        self._data = re.sub(r'\s*?titlelast', '', self._data, flags=re.I)

    def zip(self, ):
        """
        # html压缩
        :return:
        """
        self._data = re.sub('\n+', '', self._data)

    @property
    def data(self):
        return self._data


if __name__ == '__main__':
    with open('examples_html/original.html', 'r', encoding='utf-8') as f:
        data = f.read()
        data_parse = HtmlClean(data)
        data_parse.clean()
        # data_parse.zip()

    with open('examples_html/clean.html', 'w+', encoding='utf-8') as f:
        f.write(data_parse.data)
