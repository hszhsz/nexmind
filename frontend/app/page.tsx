'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Building2, TrendingUp, FileText } from 'lucide-react'
import axios from 'axios'

interface Message {
  id: string
  type: 'user' | 'bot'
  content: string
  timestamp: Date
  isLoading?: boolean
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
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    // 添加加载消息
    const loadingMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'bot',
      content: '正在分析中，请稍候...',
      timestamp: new Date(),
      isLoading: true
    }
    setMessages(prev => [...prev, loadingMessage])

    try {
      // 调用后端API
      const response = await axios.post('/api/chat', {
        message: inputValue,
        conversation_id: 'default'
      })

      // 移除加载消息并添加实际响应
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

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
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
          </div>
        </div>
      </header>

      {/* Chat Container */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full px-4 py-6">
        {/* Messages */}
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
              <div className={`flex-1 max-w-3xl ${
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

        {/* Input Area */}
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
    </div>
  )
}