from typing import Dict, List, Any, Optional
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
import asyncio
import json
from datetime import datetime
from loguru import logger

from .config import settings
from ..tools.search import SearchTool
from ..tools.analysis import AnalysisTool
from ..tools.report import ReportGenerator

class AgentState(TypedDict):
    """Agent状态定义"""
    messages: List[BaseMessage]
    query: str
    plan: List[str]
    current_step: int
    search_results: List[Dict[str, Any]]
    analysis_data: Dict[str, Any]
    final_report: str
    metadata: Dict[str, Any]

class CompanyAnalysisAgent:
    """企业分析AI Agent"""
    
    def __init__(self):
        self.llm = self._initialize_llm()
        self.search_tool = SearchTool()
        self.analysis_tool = AnalysisTool()
        self.report_generator = ReportGenerator()
        self.graph = self._build_graph()
        
    def _initialize_llm(self):
        """初始化语言模型"""
        if settings.openai_api_key:
            llm_kwargs = {
                "model": settings.openai_model,
                "temperature": settings.openai_temperature,
                "max_tokens": settings.openai_max_tokens,
                "api_key": settings.openai_api_key
            }
            
            # 如果配置了自定义base_url，则添加该参数
            if settings.openai_base_url:
                llm_kwargs["base_url"] = settings.openai_base_url
                
            return ChatOpenAI(**llm_kwargs)
        elif settings.anthropic_api_key:
            return ChatAnthropic(
                model=settings.anthropic_model,
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens,
                api_key=settings.anthropic_api_key
            )
        else:
            raise ValueError("未配置有效的AI模型API密钥")
    
    def _build_graph(self) -> StateGraph:
        """构建LangGraph工作流"""
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("searcher", self._searcher_node)
        workflow.add_node("analyzer", self._analyzer_node)
        workflow.add_node("reporter", self._reporter_node)
        
        # 设置入口点
        workflow.set_entry_point("planner")
        
        # 添加边
        workflow.add_edge("planner", "searcher")
        workflow.add_edge("searcher", "analyzer")
        workflow.add_edge("analyzer", "reporter")
        workflow.add_edge("reporter", END)
        
        return workflow.compile()
    
    async def _planner_node(self, state: AgentState) -> AgentState:
        """规划节点：制定分析计划"""
        logger.info("开始制定分析计划...")
        
        planning_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""
            你是一个专业的企业分析师。根据用户的查询，制定一个详细的分析计划。
            
            分析计划应该包括以下步骤：
            1. 公司基本信息收集
            2. 财务数据分析
            3. 行业地位评估
            4. 竞争对手分析
            5. 风险评估
            6. 投资建议
            
            请根据具体查询调整计划，并以JSON格式返回计划列表。
            """),
            HumanMessage(content=f"用户查询：{state['query']}")
        ])
        
        try:
            response = await self.llm.ainvoke(planning_prompt.format_messages())
            
            # 解析计划
            plan_text = response.content
            if "```json" in plan_text:
                plan_text = plan_text.split("```json")[1].split("```")[0]
            
            try:
                plan_data = json.loads(plan_text)
                plan = plan_data.get("plan", [])
            except json.JSONDecodeError:
                # 如果JSON解析失败，使用默认计划
                plan = [
                    "收集公司基本信息和背景",
                    "分析公司财务状况",
                    "评估行业地位和市场份额",
                    "分析主要竞争对手",
                    "识别潜在风险和机遇",
                    "生成投资建议和总结"
                ]
            
            state["plan"] = plan
            state["current_step"] = 0
            state["messages"].append(AIMessage(content=f"已制定分析计划，共{len(plan)}个步骤"))
            
            logger.info(f"分析计划制定完成，共{len(plan)}个步骤")
            return state
            
        except Exception as e:
            logger.error(f"制定分析计划时发生错误: {e}")
            # 使用默认计划
            state["plan"] = [
                "收集公司基本信息",
                "分析财务数据",
                "评估市场地位",
                "生成分析报告"
            ]
            state["current_step"] = 0
            return state
    
    async def _searcher_node(self, state: AgentState) -> AgentState:
        """搜索节点：收集相关信息"""
        logger.info("开始收集企业信息...")
        
        try:
            # 基于查询和计划进行搜索
            search_queries = self._generate_search_queries(state["query"], state["plan"])
            
            all_results = []
            # 限制并发搜索，避免过多请求
            for query in search_queries[:4]:  # 最多4个查询
                try:
                    results = await asyncio.wait_for(
                        self.search_tool.search(query, max_results=3),  # 每个查询最多3个结果
                        timeout=30  # 每个搜索30秒超时
                    )
                    all_results.extend(results)
                except asyncio.TimeoutError:
                    logger.warning(f"搜索查询超时: {query}")
                    continue
                except Exception as e:
                    logger.error(f"搜索查询失败: {query}, 错误: {e}")
                    continue
            
            state["search_results"] = all_results
            state["messages"].append(AIMessage(content=f"已收集到{len(all_results)}条相关信息"))
            
            logger.info(f"信息收集完成，共{len(all_results)}条结果")
            return state
            
        except Exception as e:
            logger.error(f"信息收集时发生错误: {e}")
            state["search_results"] = []
            return state
    
    async def _analyzer_node(self, state: AgentState) -> AgentState:
        """分析节点：分析收集的信息"""
        logger.info("开始分析企业数据...")
        
        try:
            # 使用分析工具处理搜索结果
            analysis_result = await self.analysis_tool.analyze(
                query=state["query"],
                search_results=state["search_results"],
                plan=state["plan"]
            )
            
            state["analysis_data"] = analysis_result
            state["messages"].append(AIMessage(content="企业数据分析完成"))
            
            logger.info("企业数据分析完成")
            return state
            
        except Exception as e:
            logger.error(f"数据分析时发生错误: {e}")
            state["analysis_data"] = {"error": str(e)}
            return state
    
    async def _reporter_node(self, state: AgentState) -> AgentState:
        """报告节点：生成最终报告"""
        logger.info("开始生成分析报告...")
        
        try:
            # 生成最终报告
            report = await self.report_generator.generate_report(
                query=state["query"],
                analysis_data=state["analysis_data"],
                search_results=state["search_results"]
            )
            
            state["final_report"] = report
            state["messages"].append(AIMessage(content="企业分析报告生成完成"))
            
            logger.info("分析报告生成完成")
            return state
            
        except Exception as e:
            logger.error(f"生成报告时发生错误: {e}")
            state["final_report"] = f"报告生成失败: {str(e)}"
            return state
    
    def _generate_search_queries(self, original_query: str, plan: List[str]) -> List[str]:
        """基于原始查询和计划生成搜索查询"""
        queries = [original_query]
        
        # 基于计划生成更具体的查询
        if "公司" in original_query or "企业" in original_query:
            company_name = self._extract_company_name(original_query)
            if company_name:
                queries.extend([
                    f"{company_name} 财务报表",
                    f"{company_name} 年报",
                    f"{company_name} 行业地位",
                    f"{company_name} 竞争对手"
                ])
        
        return queries[:4]  # 限制查询数量为4个
    
    def _extract_company_name(self, query: str) -> Optional[str]:
        """从查询中提取公司名称"""
        # 简单的公司名称提取逻辑
        # 在实际应用中可以使用更复杂的NLP技术
        import re
        
        # 查找可能的公司名称模式
        patterns = [
            r'([\u4e00-\u9fff]+(?:公司|集团|股份|有限|科技|实业))',
            r'([A-Za-z]+(?:\s+[A-Za-z]+)*(?:\s+(?:Inc|Corp|Ltd|Co))?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1)
        
        return None
    
    async def process_query(
        self, 
        query: str, 
        conversation_id: str = "default",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """处理用户查询"""
        logger.info(f"开始处理查询: {query}")
        
        # 初始化状态
        initial_state = AgentState(
            messages=[HumanMessage(content=query)],
            query=query,
            plan=[],
            current_step=0,
            search_results=[],
            analysis_data={},
            final_report="",
            metadata={
                "conversation_id": conversation_id,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "status": "processing"
            }
        )
        
        try:
            # 执行工作流
            final_state = await self.graph.ainvoke(initial_state)
            
            # 返回结果
            result = {
                "content": final_state["final_report"],
                "metadata": {
                    **final_state["metadata"],
                    "status": "completed",
                    "plan_steps": len(final_state["plan"]),
                    "search_results_count": len(final_state["search_results"])
                }
            }
            
            logger.info("查询处理完成")
            return result
            
        except Exception as e:
            logger.error(f"处理查询时发生错误: {e}")
            return {
                "content": f"抱歉，处理您的查询时发生了错误：{str(e)}。请稍后重试或联系技术支持。",
                "metadata": {
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat(),
                    "status": "error",
                    "error": str(e)
                }
            }