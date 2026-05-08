/**
 * CCL MindRouter - AI Orchestration Engine with Real API Integrations
 * Routes tasks to 30+ AI models and providers
 */

import axios from 'axios';

// ===== AI Provider Config =====
export interface AIProviderConfig {
  enabled: boolean;
  apiKey?: string;
  model?: string;
}

export const AI_CONFIG_KEY = 'ccl-ai-config';

// ===== Load Provider Config =====
export function loadProviderConfig(): Record<string, AIProviderConfig> {
  if (typeof window === 'undefined') return {};
  try {
    const saved = localStorage.getItem(AI_CONFIG_KEY);
    return saved ? JSON.parse(saved) : {};
  } catch {
    return {};
  }
}

// ===== Save Provider Config =====
export function saveProviderConfig(config: Record<string, AIProviderConfig>) {
  if (typeof window === 'undefined') return;
  localStorage.setItem(AI_CONFIG_KEY, JSON.stringify(config));
}

// ===== Real API Calls =====

// OpenAI
export async function callOpenAI(apiKey: string, model: string, prompt: string): Promise<string> {
  try {
    const response = await axios.post(
      'https://api.openai.com/v1/chat/completions',
      { model, messages: [{ role: 'user', content: prompt }], temperature: 0.7, max_tokens: 2000 },
      { headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' } }
    );
    return response.data.choices[0].message.content;
  } catch (error: any) {
    throw new Error(`OpenAI Error: ${error.response?.data?.error?.message || error.message}`);
  }
}

// Anthropic Claude
export async function callClaude(apiKey: string, model: string, prompt: string): Promise<string> {
  try {
    const response = await axios.post(
      'https://api.anthropic.com/v1/messages',
      { model, messages: [{ role: 'user', content: prompt }], max_tokens: 2000 },
      { headers: { 'x-api-key': apiKey, 'anthropic-version': '2023-06-01', 'Content-Type': 'application/json' } }
    );
    return response.data.content[0].text;
  } catch (error: any) {
    throw new Error(`Claude Error: ${error.response?.data?.error?.message || error.message}`);
  }
}

// Google Gemini
export async function callGemini(apiKey: string, model: string, prompt: string): Promise<string> {
  try {
    const response = await axios.post(
      `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`,
      { contents: [{ parts: [{ text: prompt }] }] },
      { headers: { 'Content-Type': 'application/json' } }
    );
    return response.data.candidates?.[0]?.content?.parts?.[0]?.text || 'No response';
  } catch (error: any) {
    throw new Error(`Gemini Error: ${error.response?.data?.error?.message || error.message}`);
  }
}

// Groq (Ultra-fast)
export async function callGroq(apiKey: string, model: string, prompt: string): Promise<string> {
  try {
    const response = await axios.post(
      'https://api.groq.com/openai/v1/chat/completions',
      { model, messages: [{ role: 'user', content: prompt }], temperature: 0.7 },
      { headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' } }
    );
    return response.data.choices[0].message.content;
  } catch (error: any) {
    throw new Error(`Groq Error: ${error.response?.data?.error?.message || error.message}`);
  }
}

// DeepSeek
export async function callDeepSeek(apiKey: string, model: string, prompt: string): Promise<string> {
  try {
    const response = await axios.post(
      'https://api.deepseek.com/v1/chat/completions',
      { model, messages: [{ role: 'user', content: prompt }], temperature: 0.7 },
      { headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' } }
    );
    return response.data.choices[0].message.content;
  } catch (error: any) {
    throw new Error(`DeepSeek Error: ${error.response?.data?.error?.message || error.message}`);
  }
}

// xAI Grok
export async function callXAI(apiKey: string, prompt: string): Promise<string> {
  try {
    const response = await axios.post(
      'https://api.x.ai/v1/chat/completions',
      { model: 'grok-1', messages: [{ role: 'user', content: prompt }], temperature: 0.7 },
      { headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' } }
    );
    return response.data.choices[0].message.content;
  } catch (error: any) {
    throw new Error(`xAI Error: ${error.response?.data?.error?.message || error.message}`);
  }
}

// Mistral AI
export async function callMistral(apiKey: string, model: string, prompt: string): Promise<string> {
  try {
    const response = await axios.post(
      'https://api.mistral.ai/v1/chat/completions',
      { model, messages: [{ role: 'user', content: prompt }], temperature: 0.7 },
      { headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' } }
    );
    return response.data.choices[0].message.content;
  } catch (error: any) {
    throw new Error(`Mistral Error: ${error.response?.data?.error?.message || error.message}`);
  }
}

// Cohere
export async function callCohere(apiKey: string, prompt: string): Promise<string> {
  try {
    const response = await axios.post(
      'https://api.cohere.ai/v1/generate',
      { model: 'command-r', prompt, max_tokens: 2000, temperature: 0.7 },
      { headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' } }
    );
    return response.data.generations?.[0]?.text || 'No response';
  } catch (error: any) {
    throw new Error(`Cohere Error: ${error.response?.data?.error?.message || error.message}`);
  }
}

// Hugging Face
export async function callHuggingFace(token: string, model: string, prompt: string): Promise<string> {
  try {
    const response = await axios.post(
      `https://api-inference.huggingface.co/models/${model}`,
      { inputs: prompt },
      { headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } }
    );
    return response.data?.[0]?.generated_text || response.data?.generated_text || 'No response';
  } catch (error: any) {
    throw new Error(`HuggingFace Error: ${error.response?.data?.error || error.message}`);
  }
}

// ===== Smart Router with Fallback =====
export async function routeToAI(task: string, taskType: string = 'general'): Promise<string> {
  const config = loadProviderConfig();
  const errors: string[] = [];
  
  // Provider order with real API calls
  const providerOrder = [
    { id: 'openai', call: () => {
      const apiKey = config['openai']?.apiKey;
      const model = config['openai']?.model || 'gpt-4-turbo';
      if (!apiKey) throw new Error('OpenAI not configured');
      return callOpenAI(apiKey, model, task);
    }},
    { id: 'anthropic', call: () => {
      const apiKey = config['anthropic']?.apiKey;
      const model = config['anthropic']?.model || 'claude-3-sonnet';
      if (!apiKey) throw new Error('Claude not configured');
      return callClaude(apiKey, model, task);
    }},
    { id: 'google', call: () => {
      const apiKey = config['google']?.apiKey;
      const model = config['google']?.model || 'gemini-pro';
      if (!apiKey) throw new Error('Gemini not configured');
      return callGemini(apiKey, model, task);
    }},
    { id: 'groq', call: () => {
      const apiKey = config['groq']?.apiKey;
      const model = config['groq']?.model || 'llama3-70b-8192';
      if (!apiKey) throw new Error('Groq not configured');
      return callGroq(apiKey, model, task);
    }},
    { id: 'deepseek', call: () => {
      const apiKey = config['deepseek']?.apiKey;
      const model = config['deepseek']?.model || 'deepseek-coder';
      if (!apiKey) throw new Error('DeepSeek not configured');
      return callDeepSeek(apiKey, model, task);
    }},
  ];
  
  for (const { id, call } of providerOrder) {
    try {
      return await call();
    } catch (error: any) {
      errors.push(`${id}: ${error.message}`);
      console.warn(`Provider ${id} failed:`, error);
    }
  }
  
  throw new Error(`All providers failed:\n${errors.join('\n')}`);
}

// ===== AI Council (Multi-AI Consensus) =====
export async function aiCouncil(task: string): Promise<Array<{provider: string, content: string, status: 'success' | 'failed', error?: string}>> {
  const config = loadProviderConfig();
  const providers = ['openai', 'anthropic', 'google', 'groq'].filter(p => config[p]?.enabled && config[p]?.apiKey);
  
  const results = await Promise.all(
    providers.map(async (providerId) => {
      try {
        const content = await routeToAI(task, 'general');
        return { provider: providerId, content, status: 'success' as const };
      } catch (error: any) {
        return { provider: providerId, content: '', status: 'failed' as const, error: error.message };
      }
    })
  );
  
  return results;
}
