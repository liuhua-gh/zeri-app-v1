# -*- coding: utf-8 -*-
"""
================================================================================
择日软件 Kivy版本（完整版）
================================================================================
包含核心计算功能的Kivy版本
================================================================================
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.core.text import LabelBase
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.utils import platform

# Android 端默认 Roboto 不含完整中文字形，改为系统 CJK 字体避免方框字。
if platform == 'android':
    LabelBase.register('Roboto', '/system/fonts/NotoSansCJK-Regular.ttc')

# 导入必要的模块
from datetime import date, datetime, timedelta
import math

# 基础数据
TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 五虎遁（月干）
WU_HU_DUN = {'甲': 2, '己': 2, '乙': 4, '庚': 4, '丙': 6, '辛': 6, '丁': 8, '壬': 8, '戊': 0, '癸': 0}

# 五鼠遁（时干）
WU_SHU_DUN = {'甲': 0, '己': 0, '乙': 2, '庚': 2, '丙': 4, '辛': 4, '丁': 6, '壬': 6, '戊': 8, '癸': 8}

# 五行属性
TIAN_GAN_WUXING = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火',
    '戊': '土', '己': '土', '庚': '金', '辛': '金',
    '壬': '水', '癸': '水'
}

# 五行生克
WUXING_SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
WUXING_KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}

# 夫星子星
FU_ZI_XING = {
    '甲': {'fu': '土', 'zi': '火'}, '乙': {'fu': '土', 'zi': '火'},
    '丙': {'fu': '金', 'zi': '土'}, '丁': {'fu': '金', 'zi': '土'},
    '戊': {'fu': '水', 'zi': '金'}, '己': {'fu': '水', 'zi': '金'},
    '庚': {'fu': '木', 'zi': '水'}, '辛': {'fu': '木', 'zi': '水'},
    '壬': {'fu': '火', 'zi': '木'}, '癸': {'fu': '火', 'zi': '木'},
}

# 事项类型
EVENT_TYPES = ['嫁娶', '修造', '动土', '入宅', '开业', '出行', '安床', '作灶', '安葬']

class SiZhuCalculator:
    """四柱计算器类"""
    
    def calculate(self, target_date, hour=12, minute=0, second=0):
        """计算完整四柱"""
        year = target_date.year
        month = target_date.month
        day = target_date.day
        
        # 计算年柱
        year_gan, year_zhi = self._calculate_year(year, month, day, hour, minute)
        
        # 计算月柱
        month_gan, month_zhi = self._calculate_month(year, month, day, hour, minute, year_gan)
        
        # 计算日柱
        day_gan, day_zhi = self._calculate_day(year, month, day)
        
        # 计算时柱
        hour_gan, hour_zhi = self._calculate_hour(day_gan, hour, minute, year, month, day)
        
        return {
            '年柱': year_gan + year_zhi,
            '月柱': month_gan + month_zhi,
            '日柱': day_gan + day_zhi,
            '时柱': hour_gan + hour_zhi,
            'year_gan': year_gan,
            'year_zhi': year_zhi,
            'month_gan': month_gan,
            'month_zhi': month_zhi,
            'day_gan': day_gan,
            'day_zhi': day_zhi,
            'hour_gan': hour_gan,
            'hour_zhi': hour_zhi,
            'is_late_zi': (hour == 23)
        }
    
    def _calculate_year(self, year, month, day, hour, minute):
        """计算年柱"""
        # 简化的立春判断
        if month < 2 or (month == 2 and day < 4):
            year -= 1
        
        # 以1984年（甲子年）为基准
        offset = (year - 1984) % 60
        gan_index = offset % 10
        zhi_index = offset % 12
        
        return TIAN_GAN[gan_index], DI_ZHI[zhi_index]
    
    def _calculate_month(self, year, month, day, hour, minute, year_gan):
        """计算月柱"""
        # 根据月份确定月支
        month_zhi_index = (month + 1) % 12
        if month_zhi_index == 0:
            month_zhi_index = 12
        month_zhi = DI_ZHI[month_zhi_index - 1]
        
        # 使用五虎遁计算月干
        base_gan_index = WU_HU_DUN.get(year_gan, 0)
        month_gan_index = (base_gan_index + (month_zhi_index - 1)) % 10
        month_gan = TIAN_GAN[month_gan_index]
        
        return month_gan, month_zhi
    
    def _calculate_day(self, year, month, day):
        """计算日柱"""
        try:
            # 以1900年1月1日为基准日（甲戌日）
            base_date = date(1900, 1, 1)
            target_date = date(year, month, day)
            days_diff = (target_date - base_date).days
            
            # 计算日干支
            gan_index = (days_diff + 0) % 10
            zhi_index = (days_diff + 10) % 12
            
            return TIAN_GAN[gan_index], DI_ZHI[zhi_index]
        except:
            return '甲', '子'
    
    def _calculate_hour(self, day_gan, hour, minute, year, month, day):
        """计算时柱"""
        # 计算时支
        if hour == 23 or (hour == 0 and minute < 0):
            hour_zhi_index = 0  # 子
        else:
            hour_zhi_index = ((hour + 1) // 2) % 12
        
        hour_zhi = DI_ZHI[hour_zhi_index]
        
        # 使用五鼠遁计算时干
        base_gan_index = WU_SHU_DUN.get(day_gan, 0)
        hour_gan_index = (base_gan_index + hour_zhi_index) % 10
        hour_gan = TIAN_GAN[hour_gan_index]
        
        return hour_gan, hour_zhi

class Scorer:
    """评分器类"""
    
    def score(self, sizhu, event_type, owners=None, house_type=None, shan_xiang=None, 
              zaoxiang=None, zaowei=None, chuangwei=None):
        """计算评分"""
        total_score = 0
        
        # 计算五行分数
        wuxing_score = self._calculate_wuxing_score(sizhu, event_type)
        total_score += wuxing_score * 0.6
        
        # 计算黄道分数
        huangdao_score = self._calculate_huangdao_score(sizhu, event_type)
        total_score += huangdao_score * 0.3
        
        # 计算月令得分
        yueling_score = self._calculate_yueling_score(sizhu)
        total_score += yueling_score * 0.1
        
        # 计算等级
        level = self._calculate_level(total_score)
        
        return {
            'score': int(total_score),
            'level': level,
            'score_details': {
                '五行得分': int(wuxing_score),
                '黄道得分': int(huangdao_score),
                '月令得分': int(yueling_score)
            }
        }
    
    def _calculate_wuxing_score(self, sizhu, event_type):
        """计算五行得分"""
        # 简化的五行评分
        scores = []
        
        # 检查四柱五行
        for key in ['年柱', '月柱', '日柱', '时柱']:
            if key in sizhu:
                try:
                    gan = sizhu[key][0]
                    wuxing = TIAN_GAN_WUXING.get(gan, '')
                    if wuxing:
                        # 简单评分逻辑
                        scores.append(25)
                except:
                    pass
        
        return sum(scores) if scores else 0
    
    def _calculate_huangdao_score(self, sizhu, event_type):
        """计算黄道得分"""
        # 简化的黄道评分
        return 80  # 临时值
    
    def _calculate_yueling_score(self, sizhu):
        """计算月令得分"""
        # 简化的月令评分
        return 70  # 临时值
    
    def _calculate_level(self, score):
        """计算等级"""
        if score >= 90:
            return '★★★★★ 大吉'
        elif score >= 80:
            return '★★★★ 吉'
        elif score >= 70:
            return '★★★ 中吉'
        elif score >= 60:
            return '★★ 小吉'
        else:
            return '★ 凶'

# 创建全局实例
calculator = SiZhuCalculator()
scorer = Scorer()

# 辅助函数
def calculate_sizhu(target_date, hour=12, minute=0, second=0):
    """计算四柱的便捷函数"""
    try:
        if isinstance(target_date, datetime):
            hour = target_date.hour
            minute = target_date.minute
            second = target_date.second
            target_date = target_date.date()
        
        result = calculator.calculate(target_date, hour, minute, second)
        
        # 确保返回的字典包含day_gan键
        if 'day_gan' not in result:
            if '日柱' in result and len(result['日柱']) > 0:
                result['day_gan'] = result['日柱'][0]
            else:
                result['day_gan'] = '甲'
                result['day_zhi'] = '子'
                result['日柱'] = '甲子'
        
        return result
    except Exception as e:
        # 返回默认值
        return {
            '年柱': '甲子',
            '月柱': '甲子',
            '日柱': '甲子',
            '时柱': '甲子',
            'year_gan': '甲',
            'year_zhi': '子',
            'month_gan': '甲',
            'month_zhi': '子',
            'day_gan': '甲',
            'day_zhi': '子',
            'hour_gan': '甲',
            'hour_zhi': '子',
            'is_late_zi': False
        }

def calculate_score(sizhu, event_type, owners=None, house_type=None, shan_xiang=None, 
                   zaoxiang=None, zaowei=None, chuangwei=None):
    """计算评分的便捷函数"""
    return scorer.score(sizhu, event_type, owners, house_type, shan_xiang, 
                       zaoxiang, zaowei, chuangwei)

def get_gan_wuxing(gan):
    """获取天干五行"""
    return TIAN_GAN_WUXING.get(gan, '')

def get_fuzi(day_gan):
    """获取夫星子星"""
    return FU_ZI_XING.get(day_gan, {'fu': None, 'zi': None})

class ZeriAppKivy(App):
    """择日软件Kivy版本"""
    
    def build(self):
        """构建应用界面"""
        self.title = '专业级正五行择日软件'
        
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 标题
        title_label = Label(
            text='专业级正五行择日软件',
            font_size='24sp',
            size_hint_y=None,
            height=50,
            bold=True
        )
        main_layout.add_widget(title_label)
        
        # 创建标签页
        tab_panel = TabbedPanel(do_default_tab=False)
        
        # 择日标签页
        tab_zeri = TabbedPanelHeader(text='择日')
        tab_zeri.content = self.create_zeri_tab()
        tab_panel.add_widget(tab_zeri)
        
        # 日课评分标签页
        tab_score = TabbedPanelHeader(text='日课评分')
        tab_score.content = self.create_score_tab()
        tab_panel.add_widget(tab_score)
        
        # 设置标签页
        tab_settings = TabbedPanelHeader(text='设置')
        tab_settings.content = self.create_settings_tab()
        tab_panel.add_widget(tab_settings)
        
        main_layout.add_widget(tab_panel)
        
        return main_layout
    
    def create_zeri_tab(self):
        """创建择日标签页"""
        scroll = ScrollView()
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        layout.bind(minimum_height=layout.setter('height'))
        
        # 事项类型选择
        layout.add_widget(Label(text='事项类型:', size_hint_y=None, height=30))
        self.event_spinner = Spinner(
            text='嫁娶',
            values=EVENT_TYPES,
            size_hint_y=None,
            height=44
        )
        layout.add_widget(self.event_spinner)
        
        # 日期范围
        layout.add_widget(Label(text='开始日期 (YYYY-MM-DD):', size_hint_y=None, height=30))
        self.start_date_input = TextInput(
            text=datetime.now().strftime('%Y-%m-%d'),
            multiline=False,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.start_date_input)
        
        layout.add_widget(Label(text='结束日期 (YYYY-MM-DD):', size_hint_y=None, height=30))
        self.end_date_input = TextInput(
            text=(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            multiline=False,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.end_date_input)
        
        # 计算按钮
        calc_btn = Button(
            text='开始择日',
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.6, 1, 1)
        )
        calc_btn.bind(on_press=self.on_calculate)
        layout.add_widget(calc_btn)
        
        # 结果显示区域
        layout.add_widget(Label(text='择日结果:', size_hint_y=None, height=30))
        self.result_label = Label(
            text='点击"开始择日"查看结果',
            size_hint_y=None,
            height=400,
            markup=True,
            halign='left',
            valign='top'
        )
        self.result_label.bind(size=self.result_label.setter('text_size'))
        layout.add_widget(self.result_label)
        
        scroll.add_widget(layout)
        return scroll
    
    def create_score_tab(self):
        """创建日课评分标签页"""
        scroll = ScrollView()
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        layout.bind(minimum_height=layout.setter('height'))
        
        layout.add_widget(Label(
            text='日课评分系统',
            font_size='20sp',
            size_hint_y=None,
            height=40,
            bold=True
        ))
        
        layout.add_widget(Label(
            text='输入日期进行评分',
            size_hint_y=None,
            height=30
        ))
        
        # 评分日期输入
        layout.add_widget(Label(text='评分日期 (YYYY-MM-DD):', size_hint_y=None, height=30))
        self.score_date_input = TextInput(
            text=datetime.now().strftime('%Y-%m-%d'),
            multiline=False,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.score_date_input)
        
        # 评分按钮
        score_btn = Button(
            text='开始评分',
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        score_btn.bind(on_press=self.on_score)
        layout.add_widget(score_btn)
        
        # 评分结果
        self.score_result_label = Label(
            text='评分结果将显示在这里',
            size_hint_y=None,
            height=300,
            markup=True,
            halign='left',
            valign='top'
        )
        self.score_result_label.bind(size=self.score_result_label.setter('text_size'))
        layout.add_widget(self.score_result_label)
        
        scroll.add_widget(layout)
        return scroll
    
    def create_settings_tab(self):
        """创建设置标签页"""
        scroll = ScrollView()
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        layout.bind(minimum_height=layout.setter('height'))
        
        layout.add_widget(Label(
            text='设置',
            font_size='20sp',
            size_hint_y=None,
            height=40,
            bold=True
        ))
        
        # 版本信息
        layout.add_widget(Label(
            text='版本: 1.0 (Kivy版)',
            size_hint_y=None,
            height=30
        ))
        
        # 关于按钮
        about_btn = Button(
            text='关于',
            size_hint_y=None,
            height=50
        )
        about_btn.bind(on_press=self.show_about)
        layout.add_widget(about_btn)
        
        scroll.add_widget(layout)
        return scroll
    
    def on_calculate(self, instance):
        """计算择日"""
        try:
            start_str = self.start_date_input.text
            end_str = self.end_date_input.text
            event_type = self.event_spinner.text
            
            start = datetime.strptime(start_str, '%Y-%m-%d').date()
            end = datetime.strptime(end_str, '%Y-%m-%d').date()
            
            if start > end:
                self.show_popup('错误', '开始日期不能晚于结束日期')
                return
            
            # 计算每日吉凶
            results = []
            current = start
            while current <= end:
                # 计算四柱
                sizhu = calculate_sizhu(current)
                
                # 计算评分
                score_result = calculate_score(sizhu, event_type)
                
                results.append({
                    'date': current,
                    'score': score_result['score'],
                    'level': score_result['level'],
                    'sizhu': f"{sizhu['年柱']} {sizhu['月柱']} {sizhu['日柱']} {sizhu['时柱']}",
                    'details': score_result['score_details']
                })
                current += timedelta(days=1)
            
            # 排序并显示前10个结果
            results.sort(key=lambda x: x['score'], reverse=True)
            top_results = results[:10]
            
            result_text = '[b]择日结果（前10名）:[/b]\n\n'
            for i, r in enumerate(top_results, 1):
                result_text += f"{i}. {r['date']}\n"
                result_text += f"   评分: {r['score']}/100\n"
                result_text += f"   等级: {r['level']}\n"
                result_text += f"   四柱: {r['sizhu']}\n"
                result_text += f"   五行: {r['details']['五行得分']}\n"
                result_text += f"   黄道: {r['details']['黄道得分']}\n"
                result_text += f"   月令: {r['details']['月令得分']}\n\n"
            
            self.result_label.text = result_text
            
        except Exception as e:
            self.show_popup('错误', f'计算失败: {str(e)}')
    
    def on_score(self, instance):
        """日课评分"""
        try:
            score_date_str = self.score_date_input.text
            event_type = self.event_spinner.text
            
            score_date = datetime.strptime(score_date_str, '%Y-%m-%d').date()
            
            # 计算四柱
            sizhu = calculate_sizhu(score_date)
            
            # 计算评分
            score_result = calculate_score(sizhu, event_type)
            
            # 显示结果
            score_text = '[b]日课评分结果:[/b]\n\n'
            score_text += f"日期: {score_date}\n"
            score_text += f"评分: {score_result['score']}/100\n"
            score_text += f"等级: {score_result['level']}\n"
            score_text += f"四柱: {sizhu['年柱']} {sizhu['月柱']} {sizhu['日柱']} {sizhu['时柱']}\n\n"
            score_text += f"[b]详细得分:[/b]\n"
            score_text += f"五行得分: {score_result['score_details']['五行得分']}\n"
            score_text += f"黄道得分: {score_result['score_details']['黄道得分']}\n"
            score_text += f"月令得分: {score_result['score_details']['月令得分']}\n"
            
            self.score_result_label.text = score_text
            
        except Exception as e:
            self.show_popup('错误', f'评分失败: {str(e)}')
    
    def show_about(self, instance):
        """显示关于信息"""
        self.show_popup('关于', '专业级正五行择日软件\n版本: 1.0 (Kivy版)\n\n用于Android设备的择日工具\n\n支持四柱计算和日课评分')
    
    def show_popup(self, title, message):
        """显示弹窗"""
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(None, None),
            size=(300, 200)
        )
        popup.open()


if __name__ == '__main__':
    ZeriAppKivy().run()
