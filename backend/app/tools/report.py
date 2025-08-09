from typing import Dict, List, Any, Optional
from langchain.schema import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from loguru import logger
from datetime import datetime
import json

from ..core.config import settings

class ReportGenerator:
    """报告生成器类"""
    
    def __init__(self):
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """初始化语言模型"""
        if settings.openai_api_key:
            llm_kwargs = {
                "model": settings.openai_model,
                "temperature": 0.2,
                "max_tokens": 4000,
                "api_key": settings.openai_api_key
            }
            
            # 如果配置了自定义base_url，则添加该参数
            if settings.openai_base_url:
                llm_kwargs["base_url"] = settings.openai_base_url
                
            return ChatOpenAI(**llm_kwargs)
        elif settings.anthropic_api_key:
            return ChatAnthropic(
                model=settings.anthropic_model,
                temperature=0.2,
                max_tokens=4000,
                api_key=settings.anthropic_api_key
            )
        else:
            raise ValueError("未配置有效的AI模型API密钥")
    
    async def generate_report(
        self, 
        query: str, 
        analysis_data: Dict[str, Any], 
        search_results: List[Dict[str, Any]]
    ) -> str:
        """生成综合分析报告"""
        logger.info("开始生成企业分析报告")
        
        try:
            # 检查分析数据是否有效
            if "error" in analysis_data:
                return self._generate_error_report(query, analysis_data["error"])
            
            # 提取关键信息
            company_name = analysis_data.get("company_name", "未知公司")
            
            # 构建报告内容
            report_sections = [
                self._generate_executive_summary(company_name, analysis_data),
                self._generate_company_overview(analysis_data.get("basic_info", {})),
                self._generate_financial_analysis_section(analysis_data.get("financial_analysis", {})),
                self._generate_industry_analysis_section(analysis_data.get("industry_analysis", {})),
                self._generate_competition_analysis_section(analysis_data.get("competition_analysis", {})),
                self._generate_risk_assessment_section(analysis_data.get("risk_assessment", {})),
                self._generate_investment_recommendation(analysis_data.get("investment_advice", {})),
                self._generate_disclaimer()
            ]
            
            # 使用AI生成最终报告
            final_report = await self._synthesize_report(company_name, report_sections, query)
            
            logger.info("企业分析报告生成完成")
            return final_report
            
        except Exception as e:
            logger.error(f"生成报告时发生错误: {e}")
            return self._generate_error_report(query, str(e))
    
    def _generate_executive_summary(self, company_name: str, analysis_data: Dict[str, Any]) -> str:
        """生成执行摘要"""
        timestamp = datetime.now().strftime("%Y年%m月%d日")
        
        summary = f"""
# {company_name} 企业分析报告

**报告日期：** {timestamp}
**分析对象：** {company_name}
**报告类型：** 综合企业分析

## 执行摘要

本报告基于公开信息和AI智能分析，对{company_name}进行了全面的企业分析。分析涵盖了公司基本情况、财务状况、行业地位、竞争环境、风险评估和投资建议等多个维度。

**关键发现：**
- 公司基本信息分析完成
- 财务状况评估完成
- 行业地位分析完成
- 竞争环境评估完成
- 风险因素识别完成
- 投资建议制定完成

---
"""
        return summary
    
    def _generate_company_overview(self, basic_info: Dict[str, Any]) -> str:
        """生成公司概况部分"""
        if not basic_info or "error" in basic_info:
            return """
## 1. 公司概况

**数据状态：** 信息收集中，建议查阅公司官方网站和最新年报获取详细信息。

---
"""
        
        section = """
## 1. 公司概况

"""
        
        # 添加基本信息
        if isinstance(basic_info, dict):
            for key, value in basic_info.items():
                if key not in ["error", "status", "note"] and value:
                    section += f"**{key}：** {value}\n\n"
        
        section += "---\n\n"
        return section
    
    def _generate_financial_analysis_section(self, financial_data: Dict[str, Any]) -> str:
        """生成财务分析部分"""
        if not financial_data or "error" in financial_data:
            return """
## 2. 财务分析

**数据状态：** 财务数据收集中，建议查阅公司最新财报获取准确的财务信息。

**分析建议：**
- 关注公司最新季报和年报
- 重点分析营收增长趋势
- 评估盈利能力和现金流状况
- 比较同行业财务指标

---
"""
        
        section = """
## 2. 财务分析

"""
        
        if isinstance(financial_data, dict):
            for key, value in financial_data.items():
                if key not in ["error", "status", "note"] and value:
                    section += f"**{key}：** {value}\n\n"
        
        section += "---\n\n"
        return section
    
    def _generate_industry_analysis_section(self, industry_data: Dict[str, Any]) -> str:
        """生成行业分析部分"""
        if not industry_data or "error" in industry_data:
            return """
## 3. 行业分析

**数据状态：** 行业信息收集中，建议关注行业研究报告和市场分析。

**分析要点：**
- 了解所属行业发展趋势
- 评估市场竞争格局
- 分析行业政策影响
- 关注技术发展动向

---
"""
        
        section = """
## 3. 行业分析

"""
        
        if isinstance(industry_data, dict):
            for key, value in industry_data.items():
                if key not in ["error", "status", "note"] and value:
                    section += f"**{key}：** {value}\n\n"
        
        section += "---\n\n"
        return section
    
    def _generate_competition_analysis_section(self, competition_data: Dict[str, Any]) -> str:
        """生成竞争分析部分"""
        if not competition_data or "error" in competition_data:
            return """
## 4. 竞争分析

**数据状态：** 竞争信息收集中，建议关注同行业公司动态和市场报告。

**分析框架：**
- 识别主要竞争对手
- 比较竞争优劣势
- 分析差异化策略
- 评估竞争威胁

---
"""
        
        section = """
## 4. 竞争分析

"""
        
        if isinstance(competition_data, dict):
            for key, value in competition_data.items():
                if key not in ["error", "status", "note"] and value:
                    section += f"**{key}：** {value}\n\n"
        
        section += "---\n\n"
        return section
    
    def _generate_risk_assessment_section(self, risk_data: Dict[str, Any]) -> str:
        """生成风险评估部分"""
        if not risk_data or "error" in risk_data:
            return """
## 5. 风险评估

**风险提示：** 投资有风险，以下为一般性风险提示：

- **市场风险：** 股价波动、市场环境变化
- **经营风险：** 业务模式、管理能力、行业周期
- **财务风险：** 资金流动性、债务水平、盈利能力
- **政策风险：** 监管政策变化、行业政策调整
- **其他风险：** 技术变革、竞争加剧、不可抗力

**建议：** 投资前请详细了解相关风险，并根据自身风险承受能力做出投资决策。

---
"""
        
        section = """
## 5. 风险评估

"""
        
        if isinstance(risk_data, dict):
            for key, value in risk_data.items():
                if key not in ["error", "status", "note"] and value:
                    section += f"**{key}：** {value}\n\n"
        
        section += "---\n\n"
        return section
    
    def _generate_investment_recommendation(self, investment_data: Dict[str, Any]) -> str:
        """生成投资建议部分"""
        if not investment_data or "error" in investment_data:
            return """
## 6. 投资建议

**重要声明：** 以下建议仅供参考，不构成投资建议。投资决策应基于您自己的研究和风险评估。

**一般性建议：**
- 深入研究公司基本面
- 关注行业发展趋势
- 评估估值水平合理性
- 考虑投资时间周期
- 分散投资降低风险

**建议投资者：**
- 查阅公司最新财报和公告
- 关注行业研究报告
- 咨询专业投资顾问
- 根据自身情况制定投资策略

---
"""
        
        section = """
## 6. 投资建议

**重要声明：** 以下分析仅供参考，不构成投资建议。

"""
        
        if isinstance(investment_data, dict):
            for key, value in investment_data.items():
                if key not in ["error", "status", "note"] and value:
                    section += f"**{key}：** {value}\n\n"
        
        section += "---\n\n"
        return section
    
    def _generate_disclaimer(self) -> str:
        """生成免责声明"""
        return """
## 免责声明

1. **信息来源：** 本报告基于公开信息和AI智能分析生成，信息的准确性和完整性可能受到限制。

2. **投资风险：** 投资有风险，过往业绩不代表未来表现。投资者应根据自身情况谨慎决策。

3. **专业建议：** 本报告不构成投资建议，如需投资决策，请咨询专业的投资顾问。

4. **信息更新：** 市场信息瞬息万变，建议关注公司最新公告和市场动态。

5. **法律责任：** 使用本报告所产生的任何损失，本系统不承担法律责任。

---

**报告生成时间：** {}
**技术支持：** NexMind AI 企业分析平台
""".format(datetime.now().strftime("%Y年%m月%d日 %H:%M:%S"))
    
    def _generate_error_report(self, query: str, error_message: str) -> str:
        """生成错误报告"""
        timestamp = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        
        return f"""
# 企业分析报告

**查询内容：** {query}
**报告时间：** {timestamp}
**状态：** 分析遇到问题

## 分析状态

抱歉，在分析过程中遇到了一些问题：{error_message}

## 建议

1. **检查查询内容：** 请确保公司名称正确且为中国境内公司
2. **稍后重试：** 系统可能暂时繁忙，请稍后再试
3. **手动查询：** 建议您直接查阅以下官方渠道：
   - 公司官方网站
   - 证券交易所公告
   - 财经新闻网站
   - 行业研究报告

## 联系支持

如果问题持续存在，请联系技术支持团队。

---

**技术支持：** NexMind AI 企业分析平台
"""
    
    async def _synthesize_report(self, company_name: str, sections: List[str], original_query: str) -> str:
        """使用AI合成最终报告"""
        try:
            # 合并所有部分
            raw_report = "\n".join(sections)
            
            # 使用AI优化报告
            synthesis_prompt = f"""
            请优化以下企业分析报告，使其更加专业、连贯和易读。保持所有重要信息，但改善表达方式和结构。
            
            原始查询：{original_query}
            公司名称：{company_name}
            
            原始报告：
            {raw_report}
            
            请生成一份专业的企业分析报告，要求：
            1. 保持所有重要信息和数据
            2. 改善语言表达和逻辑结构
            3. 确保专业性和可读性
            4. 保留所有免责声明
            5. 使用Markdown格式
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content="你是一个专业的企业分析报告撰写专家，擅长将分析数据整合成专业、易读的报告。"),
                HumanMessage(content=synthesis_prompt)
            ])
            
            return response.content
            
        except Exception as e:
            logger.error(f"合成报告时发生错误: {e}")
            # 如果AI合成失败，返回原始报告
            return "\n".join(sections)