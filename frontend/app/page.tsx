'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Building2, TrendingUp, FileText, Search, Database, Brain, CheckCircle, Clock, AlertCircle } from 'lucide-react'
import axios from 'axios'

interface Message {
  id: string
  type: 'user' | 'bot'
  content: string
  timestamp: Date
  isLoading?: boolean
}

interface AgentAction {
  id: string
  type: 'search' | 'analyze' | 'generate' | 'complete'
  title: string
  description: string
  status: 'pending' | 'running' | 'completed' | 'error'
  timestamp: Date
  duration?: number
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'bot',
      content: '您好！我是NexMind智能分析助手。请告诉我您想了解哪家中国公司的详细信息，我将为您生成comprehensive的企业分析报告。',
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [agentActions, setAgentActions] = useState<AgentAction[]>([])
  const [showAgentPanel, setShowAgentPanel] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const actionsEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const scrollActionsToBottom = () => {
    actionsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    scrollActionsToBottom()
  }, [agentActions])

  const simulateAgentActions = (query: string) => {
    setShowAgentPanel(true)
    setAgentActions([])
    
    const actions = [
      {
        type: 'search' as const,
        title: '搜索企业信息',
        description: `正在搜索"${query}"的相关企业数据...`,
        status: 'pending' as const
      },
      {
        type: 'analyze' as const,
        title: '数据分析',
        description: '分析企业财务数据、市场表现和行业地位...',
        status: 'pending' as const
      },
      {
        type: 'generate' as const,
        title: '生成报告',
        description: '基于分析结果生成comprehensive企业分析报告...',
        status: 'pending' as const
      }
    ]

    actions.forEach((action, index) => {
      setTimeout(() => {
        const newAction: AgentAction = {
          ...action,
          id: `action-${Date.now()}-${index}`,
          timestamp: new Date(),
          status: 'running'
        }
        setAgentActions(prev => [...prev, newAction])

        setTimeout(() => {
          setAgentActions(prev => 
            prev.map(a => 
              a.id === newAction.id 
                ? { ...a, status: 'completed' as const, duration: Math.floor(Math.random() * 3000) + 1000 }
                : a
            )
          )
        }, Math.random() * 2000 + 1000)
      }, index * 800)
    })
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    }

    const currentQuery = inputValue
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    simulateAgentActions(currentQuery)

    const loadingMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'bot',
      content: '正在分析中，请稍候...',
      timestamp: new Date(),
      isLoading: true
    }
    setMessages(prev => [...prev, loadingMessage])

    try {
      const response = await axios.post('/api/chat', {
        message: currentQuery,
        conversation_id: 'default'
      })

      setMessages(prev => {
        const filtered = prev.filter(msg => !msg.isLoading)
        return [...filtered, {
          id: (Date.now() + 2).toString(),
          type: 'bot',
          content: response.data.response || '抱歉，我暂时无法处理您的请求。请稍后再试。',
          timestamp: new Date()
        }]
      })
    } catch (error) {
      console.error('Error sending message:', error)
      setMessages(prev => {
        const filtered = prev.filter(msg => !msg.isLoading)
        return [...filtered, {
          id: (Date.now() + 2).toString(),
          type: 'bot',
          content: '抱歉，服务暂时不可用。请检查后端服务是否正常运行。',
          timestamp: new Date()
        }]
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const getActionIcon = (type: AgentAction['type']) => {
    switch (type) {
      case 'search': return <Search className="w-4 h-4" />
      case 'analyze': return <Database className="w-4 h-4" />
      case 'generate': return <Brain className="w-4 h-4" />
      default: return <CheckCircle className="w-4 h-4" />
    }
  }

  const getStatusIcon = (status: AgentAction['status']) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'running': return <Clock className="w-4 h-4 text-blue-500 animate-spin" />
      case 'error': return <AlertCircle className="w-4 h-4 text-red-500" />
      default: return <Clock className="w-4 h-4 text-gray-400" />
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Building2 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">NexMind</h1>
              <p className="text-sm text-gray-600">智能企业分析平台</p>
            </div>
          </div>
          <div className="flex items-center space-x-6 text-sm text-gray-600">
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-4 h-4" />
              <span>实时数据</span>
            </div>
            <div className="flex items-center space-x-2">
              <FileText className="w-4 h-4" />
              <span>AI分析</span>
            </div>
            {showAgentPanel && (
              <button
                onClick={() => setShowAgentPanel(!showAgentPanel)}
                className="flex items-center space-x-2 px-3 py-1 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
              >
                <Brain className="w-4 h-4" />
                <span>Agent动作</span>
              </button>
            )}
          </div>
        </div>
      </header>

      <div className="flex-1 flex max-w-7xl mx-auto w-full">
        <div className={`flex-1 flex flex-col px-4 py-6 transition-all duration-300 ${
          showAgentPanel ? 'mr-2' : ''
        }`}>
          <div className="flex-1 overflow-y-auto space-y-4 mb-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-start space-x-3 message-animation ${
                  message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                }`}
              >
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.type === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 text-gray-600'
                }`}>
                  {message.type === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>
                <div className={`flex-1 ${
                  showAgentPanel ? 'max-w-2xl' : 'max-w-3xl'
                } ${
                  message.type === 'user' ? 'text-right' : 'text-left'
                }`}>
                  <div className={`inline-block px-4 py-3 rounded-2xl ${
                    message.type === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white border border-gray-200 text-gray-900'
                  } ${message.isLoading ? 'loading-pulse' : ''}`}>
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  </div>
                  <p className="text-xs text-gray-500 mt-1 px-2">
                    {message.timestamp.toLocaleTimeString('zh-CN', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          <div className="bg-white rounded-2xl border border-gray-200 shadow-lg p-4">
            <div className="flex items-end space-x-3">
              <div className="flex-1">
                <textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="请输入您想了解的公司名称或相关问题..."
                  className="w-full resize-none border-0 focus:ring-0 focus:outline-none text-gray-900 placeholder-gray-500"
                  rows={1}
                  style={{ minHeight: '24px', maxHeight: '120px' }}
                  disabled={isLoading}
                />
              </div>
              <button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isLoading}
                className="flex-shrink-0 w-10 h-10 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-xl flex items-center justify-center transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
            <div className="flex items-center justify-between mt-3 text-xs text-gray-500">
              <span>按 Enter 发送，Shift + Enter 换行</span>
              <span>由 AI 驱动的企业分析</span>
            </div>
          </div>
        </div>

        {showAgentPanel && (
          <div className="w-80 border-l border-gray-200 bg-gray-50 flex flex-col agent-panel-enter">
            <div className="p-4 border-b border-gray-200 bg-white">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
                  <Brain className="w-5 h-5 text-blue-600" />
                  <span>Agent 执行过程</span>
                </h3>
                <button
                  onClick={() => setShowAgentPanel(false)}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  ×
                </button>
              </div>
              <p className="text-sm text-gray-600 mt-1">实时查看AI分析过程</p>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {agentActions.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <Brain className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <p>发送消息后查看Agent执行过程</p>
                </div>
              ) : (
                agentActions.map((action) => (
                  <div
                    key={action.id}
                    className={`bg-white rounded-lg p-3 border transition-all duration-300 action-item-enter ${
                      action.status === 'completed' ? 'border-green-200 bg-green-50' :
                      action.status === 'running' ? 'border-blue-200 bg-blue-50' :
                      action.status === 'error' ? 'border-red-200 bg-red-50' :
                      'border-gray-200'
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                        action.status === 'completed' ? 'bg-green-100 text-green-600' :
                        action.status === 'running' ? 'bg-blue-100 text-blue-600' :
                        action.status === 'error' ? 'bg-red-100 text-red-600' :
                        'bg-gray-100 text-gray-600'
                      }`}>
                        {getActionIcon(action.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <h4 className="text-sm font-medium text-gray-900 truncate">
                            {action.title}
                          </h4>
                          <div className={action.status === 'completed' ? 'status-completed' : ''}>
                            {getStatusIcon(action.status)}
                          </div>
                        </div>
                        <p className="text-xs text-gray-600 mt-1">
                          {action.description}
                        </p>
                        <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                          <span>
                            {action.timestamp.toLocaleTimeString('zh-CN', {
                              hour: '2-digit',
                              minute: '2-digit',
                              second: '2-digit'
                            })}
                          </span>
                          {action.duration && action.status === 'completed' && (
                            <span className="text-green-600">
                              耗时 {(action.duration / 1000).toFixed(1)}s
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
              <div ref={actionsEndRef} />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}