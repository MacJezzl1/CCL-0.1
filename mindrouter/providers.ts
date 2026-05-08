/**
 * CCL MindRouter - Real AI API Integrations
 * Connects to 30+ AI models with fallback support
 */

import axios from 'axios';

// ===== OpenAI Integration =====
export async function callOpenAI(apiKey: string, model: string, prompt: string): Promise<string> {
    try {
        const response = await axios.post(
            'https://api.openai.com/v1/chat/completions',
            {
                model: model,
                messages: [{ role: 'user', content: prompt }],
                temperature: 0.7,
                max_tokens: 2000,
            },
            {
                headers: {
                    'Authorization': `Bearer ${apiKey}`,
                    'Content-Type': 'application/json',
                },
            }
        );

        return response.data.choices[0].message.content;
    } catch (error: any) {
        throw new Error(`OpenAI API Error: ${error.response?.data?.error?.message || error.message}`);
    }
}

// ===== Anthropic Claude Integration =====
export async function callClaude(apiKey: string, model: string, prompt: string): Promise<string> {
    try {
        const response = await axios.post(
            'https://api.anthropic.com/v1/messages',
            {
                model: model,
                messages: [{ role: 'user', content: prompt }],
                max_tokens: 2000,
            },
            {
                headers: {
                    'x-api-key': apiKey,
                    'anthropic-version': '2023-06-01',
                    'Content-Type': 'application/json',
                },
            }
        );

        return response.data.content[0].text;
    } catch (error: any) {
        throw new Error(`Claude API Error: ${error.response?.data?.error?.message || error.message}`);
    }
}

// ===== Google Gemini Integration =====
export async function callGemini(apiKey: string, model: string, prompt: string): Promise<string> {
    try {
        const response = await axios.post(
            `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`,
            {
                contents: [{ parts: [{ text: prompt }] }],
            },
            {
                headers: {
                    'Content-Type': 'application/json',
                },
            }
        );

        return response.data.candidates[0].content.parts[0].text;
    } catch (error: any) {
        throw new Error(`Gemini API Error: ${error.response?.data?.error?.message || error.message}`);
    }
}

// ===== Groq Integration (Ultra-fast) =====
export async function callGroq(apiKey: string, model: string, prompt: string): Promise<string> {
    try {
        const response = await axios.post(
            'https://api.groq.com/openai/v1/chat/completions',
            {
                model: model,
                messages: [{ role: 'user', content: prompt }],
                temperature: 0.7,
            },
            {
                headers: {
                    'Authorization': `Bearer ${apiKey}`,
                    'Content-Type': 'application/json',
                },
            }
        );

        return response.data.choices[0].message.content;
    } catch (error: any) {
        throw new Error(`Groq API Error: ${error.response?.data?.error?.message || error.message}`);
    }
}

// ===== DeepSeek Integration =====
export async function callDeepSeek(apiKey: string, model: string, prompt: string): Promise<string> {
    try {
        const response = await axios.post(
            'https://api.deepseek.com/v1/chat/completions',
            {
                model: model,
                messages: [{ role: 'user', content: prompt }],
                temperature: 0.7,
            },
            {
                headers: {
                    'Authorization': `Bearer ${apiKey}`,
                    'Content-Type': 'application/json',
                },
            }
        );

        return response.data.choices[0].message.content;
    } catch (error: any) {
        throw new Error(`DeepSeek API Error: ${error.response?.data?.error?.message || error.message}`);
    }
}

// ===== xAI Grok Integration =====
export async function callXAI(apiKey: string, prompt: string): Promise<string> {
    try {
        const response = await axios.post(
            'https://api.x.ai/v1/chat/completions',
            {
                model: 'grok-1',
                messages: [{ role: 'user', content: prompt }],
                temperature: 0.7,
            },
            {
                headers: {
                    'Authorization': `Bearer ${apiKey}`,
                    'Content-Type': 'application/json',
                },
            }
        );

        return response.data.choices[0].message.content;
    } catch (error: any) {
        throw new Error(`xAI API Error: ${error.response?.data?.error?.message || error.message}`);
    }
}

// ===== Mistral AI Integration =====
export async function callMistral(apiKey: string, model: string, prompt: string): Promise<string> {
    try {
        const response = await axios.post(
            'https://api.mistral.ai/v1/chat/completions',
            {
                model: model,
                messages: [{ role: 'user', content: prompt }],
                temperature: 0.7,
            },
            {
                headers: {
                    'Authorization': `Bearer ${apiKey}`,
                    'Content-Type': 'application/json',
                },
            }
        );

        return response.data.choices[0].message.content;
    } catch (error: any) {
        throw new Error(`Mistral API Error: ${error.response?.data?.error?.message || error.message}`);
    }
}

// ===== Cohere Integration =====
export async function callCohere(apiKey: string, prompt: string): Promise<string> {
    try {
        const response = await axios.post(
            'https://api.cohere.ai/v1/generate',
            {
                model: 'command-r',
                prompt: prompt,
                max_tokens: 2000,
                temperature: 0.7,
            },
            {
                headers: {
                    'Authorization': `Bearer ${apiKey}`,
                    'Content-Type': 'application/json',
                },
            }
        );

        return response.data.generations[0].text;
    } catch (error: any) {
        throw new Error(`Cohere API Error: ${error.response?.data?.error?.message || error.message}`);
    }
}

// ===== Hugging Face Inference API =====
export async function callHuggingFace(token: string, model: string, prompt: string): Promise<string> {
    try {
        const response = await axios.post(
            `https://api-inference.huggingface.co/models/${model}`,
            { inputs: prompt },
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
            }
        );

        return response.data[0]?.generated_text || response.data.generated_text || 'No response';
    } catch (error: any) {
        throw new Error(`Hugging Face API Error: ${error.response?.data?.error || error.message}`);
    }
}

// ===== Export all providers =====
export const AIProviders = {
    openai: callOpenAI,
    anthropic: callClaude,
    google: callGemini,
    groq: callGroq,
    deepseek: callDeepSeek,
    xai: callXAI,
    mistral: callMistral,
    cohere: callCohere,
    huggingface: callHuggingFace,
};

// ===== Smart Router with Fallback =====
export async function smartRoute(providerCallbacks: Array<() => Promise<string>>, prompt: string): Promise<string> {
    let lastError: Error | null = null;

    for (const callback of providerCallbacks) {
        try {
            return await callback();
        } catch (error) {
            lastError = error as Error;
            console.warn(`Provider failed, trying next: ${error}`);
        }
    }

    throw lastError || new Error('All providers failed');
}
