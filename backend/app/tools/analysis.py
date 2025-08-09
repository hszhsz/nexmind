from typing import Dict, List, Any, Optional
from langchain.schema import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from loguru import logger
import json
import re
from datetime import datetime

from ..core.config import settings

class AnalysisTool:
    """企业分析工具类"""
    
    def __init__(self):
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """初始化语言模型"""
        if settings.openai_api_key:
            llm_kwargs = {
                "model": settings.openai_model,
                "temperature": 0.1,
                "max_tokens": 2000,
                "api_key": settings.openai_api_key
            }
            
            # 如果配置了自定义base_url，则添加该参数
            if settings.openai_base_url:
                llm_kwargs["base_url"] = settings.openai_base_url
                
            return ChatOpenAI(**llm_kwargs)
        elif settings.anthropic_api_key:
            return ChatAnthropic(
                model=settings.anthropic_model,
                temperature=0.1,
                max_tokens=2000,
                api_key=settings.anthropic_api_key
            )
        else:
            raise ValueError("未配置有效的AI模型API密钥")
    
    async def analyze(
        self, 
        query: str, 
        search_results: List[Dict[str, Any]], 
        plan: List[str]
    ) -> Dict[str, Any]:
        """分析企业数据"""
        logger.info("开始分析企业数据")
        
        try:
            # 提取公司名称
            company_name = self._extract_company_name(query)
            
            # 分析基本信息
            basic_info = await self._analyze_basic_info(company_name, search_results)
            
            # 分析财务状况
            financial_analysis = await self._analyze_financial_data(company_name, search_results)
            
            # 分析行业地位
            industry_analysis = await self._analyze_industry_position(company_name, search_results)
            
            # 分析竞争态势
            competition_analysis = await self._analyze_competition(company_name, search_results)
            
            # 风险评估
            risk_assessment = await self._assess_risks(company_name, search_results)
            
            # 投资建议
            investment_advice = await self._generate_investment_advice(company_name, search_results)
            
            analysis_result = {
                "company_name": company_name,
                "basic_info": basic_info,
                "financial_analysis": financial_analysis,
                "industry_analysis": industry_analysis,
                "competition_analysis": competition_analysis,
                "risk_assessment": risk_assessment,
                "investment_advice": investment_advice,
                "analysis_timestamp": datetime.now().isoformat(),
                "data_sources": len(search_results)
            }
            
            logger.info("企业数据分析完成")
            return analysis_result
            
        except Exception as e:
            logger.error(f"分析企业数据时发生错误: {e}")
            return {
                "error": str(e),
                "company_name": self._extract_company_name(query),
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    def _extract_company_name(self, query: str) -> str:
        """从查询中提取公司名称"""
        # 简单的公司名称提取逻辑
        patterns = [
            r'([\u4e00-\u9fff]+(?:公司|集团|股份|有限|科技|实业|银行|保险|证券))',
            r'([A-Za-z]+(?:\s+[A-Za-z]+)*(?:\s+(?:Inc|Corp|Ltd|Co|Group|Holdings))?)',
            r'([\u4e00-\u9fff]{2,10})(?=的|怎么样|如何|分析)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1).strip()
        
        # 如果没有匹配到，返回查询的前几个词
        words = query.split()[:3]
        return ' '.join(words)
    
    async def _analyze_basic_info(self, company_name: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析公司基本信息"""
        try:
            # 整合搜索结果
            context = self._prepare_context(search_results)
            
            prompt = f"""
            基于以下信息，分析{company_name}的基本情况：
            
            {context}
            
            请提供以下信息（如果信息不足，请标注"信息不足"）：
            1. 公司全称和简介
            2. 成立时间和注册地
            3. 主营业务和产品
            4. 公司规模（员工数量、注册资本等）
            5. 上市情况（股票代码、上市交易所）
            
            请以JSON格式返回结果。
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content="你是一个专业的企业分析师，擅长从各种信息中提取和分析企业基本信息。"),
                HumanMessage(content=prompt)
            ])
            
            # 解析响应
            result = self._parse_json_response(response.content)
            return result if result else {
                "company_name": company_name,
                "status": "信息不足",
                "note": "无法获取足够的基本信息"
            }
            
        except Exception as e:
            logger.error(f"分析基本信息时发生错误: {e}")
            return {"error": str(e)}
    
    async def _analyze_financial_data(self, company_name: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析财务数据"""
        try:
            context = self._prepare_context(search_results, keywords=["财务", "营收", "利润", "资产", "负债"])
            
            prompt = f"""
            基于以下信息，分析{company_name}的财务状况：
            
            {context}
            
            请分析以下财务指标（如果信息不足，请标注"信息不足"）：
            1. 营业收入趋势
            2. 净利润情况
            3. 资产负债状况
            4. 现金流情况
            5. 主要财务比率（ROE、ROA、负债率等）
            6. 财务健康度评估
            
            请以JSON格式返回结果。
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content="你是一个专业的财务分析师，擅长分析企业财务数据和财务健康状况。"),
                HumanMessage(content=prompt)
            ])
            
            result = self._parse_json_response(response.content)
            return result if result else {
                "status": "信息不足",
                "note": "无法获取足够的财务信息"
            }
            
        except Exception as e:
            logger.error(f"分析财务数据时发生错误: {e}")
            return {"error": str(e)}
    
    async def _analyze_industry_position(self, company_name: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析行业地位"""
        try:
            context = self._prepare_context(search_results, keywords=["行业", "市场", "排名", "份额", "地位"])
            
            prompt = f"""
            基于以下信息，分析{company_name}的行业地位：
            
            {context}
            
            请分析以下方面（如果信息不足，请标注"信息不足"）：
            1. 所属行业和细分领域
            2. 市场份额和排名
            3. 行业地位和竞争优势
            4. 行业发展趋势
            5. 公司在行业中的创新能力
            
            请以JSON格式返回结果。
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content="你是一个专业的行业分析师，擅长分析企业在行业中的地位和竞争优势。"),
                HumanMessage(content=prompt)
            ])
            
            result = self._parse_json_response(response.content)
            return result if result else {
                "status": "信息不足",
                "note": "无法获取足够的行业信息"
            }
            
        except Exception as e:
            logger.error(f"分析行业地位时发生错误: {e}")
            return {"error": str(e)}
    
    async def _analyze_competition(self, company_name: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析竞争态势"""
        try:
            context = self._prepare_context(search_results, keywords=["竞争", "对手", "比较", "优势", "劣势"])
            
            prompt = f"""
            基于以下信息，分析{company_name}的竞争态势：
            
            {context}
            
            请分析以下方面（如果信息不足，请标注"信息不足"）：
            1. 主要竞争对手
            2. 竞争优势和劣势
            3. 差异化策略
            4. 市场竞争格局
            5. 竞争威胁评估
            
            请以JSON格式返回结果。
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content="你是一个专业的竞争分析师，擅长分析企业竞争环境和竞争策略。"),
                HumanMessage(content=prompt)
            ])
            
            result = self._parse_json_response(response.content)
            return result if result else {
                "status": "信息不足",
                "note": "无法获取足够的竞争信息"
            }
            
        except Exception as e:
            logger.error(f"分析竞争态势时发生错误: {e}")
            return {"error": str(e)}
    
    async def _assess_risks(self, company_name: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """评估风险"""
        try:
            context = self._prepare_context(search_results, keywords=["风险", "挑战", "问题", "监管", "政策"])
            
            prompt = f"""
            基于以下信息，评估{company_name}面临的风险：
            
            {context}
            
            请评估以下风险类型（如果信息不足，请标注"信息不足"）：
            1. 财务风险
            2. 经营风险
            3. 市场风险
            4. 政策监管风险
            5. 技术风险
            6. 整体风险等级评估
            
            请以JSON格式返回结果。
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content="你是一个专业的风险分析师，擅长识别和评估企业面临的各种风险。"),
                HumanMessage(content=prompt)
            ])
            
            result = self._parse_json_response(response.content)
            return result if result else {
                "status": "信息不足",
                "note": "无法获取足够的风险信息"
            }
            
        except Exception as e:
            logger.error(f"评估风险时发生错误: {e}")
            return {"error": str(e)}
    
    async def _generate_investment_advice(self, company_name: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成投资建议"""
        try:
            context = self._prepare_context(search_results, keywords=["投资", "价值", "前景", "建议", "评级"])
            
            prompt = f"""
            基于以下信息，为{company_name}提供投资建议：
            
            {context}
            
            请提供以下投资分析（如果信息不足，请标注"信息不足"）：
            1. 投资价值评估
            2. 投资建议（买入/持有/卖出）
            3. 目标价格区间（如适用）
            4. 投资亮点
            5. 投资风险提示
            6. 适合的投资者类型
            
            请以JSON格式返回结果。
            """
            
            response = await self.llm.ainvoke([
                SystemMessage(content="你是一个专业的投资分析师，擅长评估企业投资价值并提供投资建议。请注意，所有建议仅供参考，投资有风险。"),
                HumanMessage(content=prompt)
            ])
            
            result = self._parse_json_response(response.content)
            return result if result else {
                "status": "信息不足",
                "note": "无法获取足够的投资信息"
            }
            
        except Exception as e:
            logger.error(f"生成投资建议时发生错误: {e}")
            return {"error": str(e)}
    
    def _prepare_context(self, search_results: List[Dict[str, Any]], keywords: Optional[List[str]] = None) -> str:
        """准备分析上下文"""
        if not search_results:
            return "暂无相关信息"
        
        context_parts = []
        for i, result in enumerate(search_results[:10]):  # 限制结果数量
            title = result.get('title', '')
            content = result.get('content', '')
            source = result.get('source', '')
            
            # 如果指定了关键词，优先选择包含关键词的内容
            if keywords:
                if not any(keyword in title + content for keyword in keywords):
                    continue
            
            context_parts.append(f"信息{i+1}：\n标题：{title}\n内容：{content[:500]}...\n来源：{source}\n")
        
        return "\n".join(context_parts) if context_parts else "暂无相关信息"
    
    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """解析JSON响应"""
        try:
            # 尝试直接解析
            if response.startswith('{') and response.endswith('}'):
                return json.loads(response)
            
            # 查找JSON代码块
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                if json_end != -1:
                    json_str = response[json_start:json_end].strip()
                    return json.loads(json_str)
            
            # 查找花括号内容
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            
            return None
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败: {e}")
            return None
        except Exception as e:
            logger.error(f"解析响应时发生错误: {e}")
            return None