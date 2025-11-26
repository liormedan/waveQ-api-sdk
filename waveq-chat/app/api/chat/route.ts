import { openai } from '@ai-sdk/openai';
import { convertToCoreMessages, streamText, tool } from 'ai';
import { z } from 'zod';

// Allow streaming responses up to 30 seconds
export const maxDuration = 30;

const WAVEQ_API_URL = process.env.WAVEQ_API_URL || 'http://localhost:8000';
const WAVEQ_API_KEY = process.env.WAVEQ_API_KEY || 'waveq_demo_key_123';

// Helper function to call WaveQ API
async function callWaveQAPI(endpoint: string, formData: FormData) {
    const response = await fetch(`${WAVEQ_API_URL}${endpoint}`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${WAVEQ_API_KEY}`,
        },
        body: formData,
    });

    if (!response.ok) {
        throw new Error(`WaveQ API error: ${response.statusText}`);
    }

    return await response.json();
}

export async function POST(req: Request) {
    const { messages } = await req.json();

    const result = streamText({
        model: openai('gpt-4-turbo'),
        messages: convertToCoreMessages(messages),
        system: `אתה סוכן AI מומחה בעיבוד אודיו בשם WaveQ.

אתה יכול לעזור למשתמשים עם:
- ניקוי רעש מאודיו (denoise)
- המרת דיבור לטקסט עם זיהוי דוברים (transcribe)
- חיתוך והסרת שקט (trim)
- הפרדת ווקלים/כלי נגינה (separate)
- ניתוח סנטימנט ורגשות (analyze sentiment)
- המרת טקסט לדיבור (text-to-speech)

כשמשתמש מעלה קובץ או מבקש פעולה על אודיו, השתמש בכלים המתאימים.
תמיד תהיה ידידותי, עוזר ומקצועי. ענה בעברית אלא אם המשתמש מבקש אחרת.

כשמשתמש מבקש מספר פעולות (למשל "תנקה ותמלל"), תקרא לכל הכלים בנפרד.
`,
        tools: {
            denoise_audio: tool({
                description: 'הסר רעש רקע ושפר איכות אודיו. השתמש כשהמשתמש רוצה לנקות או להסיר רעש.',
                parameters: z.object({
                    fileId: z.string().describe('מזהה הקובץ להעלאה'),
                    noiseLevel: z.number().min(0).max(1).default(0.8).describe('עוצמת הפחתת הרעש (0-1)'),
                }),
                execute: async ({ fileId, noiseLevel }) => {
                    try {
                        // In real implementation - fetch file from uploads, process via WaveQ API
                        return {
                            status: 'processing',
                            taskId: `task_${Date.now()}`,
                            message: `מעבד... מסיר רעש ברמה ${Math.round(noiseLevel * 100)}%`,
                            operation: 'denoise',
                        };
                    } catch (error) {
                        return {
                            status: 'failed',
                            error: 'שגיאה בניקוי האודיו',
                        };
                    }
                },
            }),

            transcribe_audio: tool({
                description: 'המר דיבור לטקסט עם אפשרות לזיהוי דוברים. השתמש כשהמשתמש רוצה תמלול.',
                parameters: z.object({
                    fileId: z.string().describe('מזהה הקובץ לתמלול'),
                    language: z.string().optional().describe('קוד שפה (למשל "he" לעברית, "en" לאנגלית)'),
                    enableDiarization: z.boolean().default(false).describe('האם לזהות דוברים שונים'),
                }),
                execute: async ({ fileId, language, enableDiarization }) => {
                    return {
                        status: 'processing',
                        taskId: `task_${Date.now()}`,
                        message: `מתמלל${enableDiarization ? ' עם זיהוי דוברים' : ''}...`,
                        operation: 'transcribe',
                    };
                },
            }),

            trim_audio: tool({
                description: 'הסר שקט וחתוך אודיו. השתמש כשהמשתמש רוצה להסיר חלקים שקטים או לחתוך.',
                parameters: z.object({
                    fileId: z.string().describe('מזהה הקובץ לחיתוך'),
                    silenceThreshold: z.number().default(-40).describe('סף השקט בdB'),
                }),
                execute: async ({ fileId, silenceThreshold }) => {
                    return {
                        status: 'processing',
                        taskId: `task_${Date.now()}`,
                        message: 'מסיר שקט וחותך...',
                        operation: 'trim',
                    };
                },
            }),

            separate_audio: tool({
                description: 'הפרד ווקלים מכלי נגינה או בודד מקורות אודיו. השתמש כשהמשתמש רוצה להפריד vocals, תופים, בס וכו\'.',
                parameters: z.object({
                    fileId: z.string().describe('מזהה הקובץ להפרדה'),
                    separationType: z.enum(['vocals', 'drums', 'bass', 'other']).default('vocals').describe('סוג ההפרדה'),
                }),
                execute: async ({ fileId, separationType }) => {
                    const typeNames: Record<string, string> = {
                        vocals: 'ווקלים',
                        drums: 'תופים',
                        bass: 'בס',
                        other: 'אחר',
                    };
                    return {
                        status: 'processing',
                        taskId: `task_${Date.now()}`,
                        message: `מפריד ${typeNames[separationType]}...`,
                        operation: 'separate',
                    };
                },
            }),

            analyze_sentiment: tool({
                description: 'נתח סנטימנט ורגשות באודיו. השתמש כשהמשתמש רוצה לדעת את הטון הרגשי.',
                parameters: z.object({
                    fileId: z.string().describe('מזהה הקובץ לניתוח'),
                }),
                execute: async ({ fileId }) => {
                    return {
                        status: 'processing',
                        taskId: `task_${Date.now()}`,
                        message: 'מנתח סנטימנט ורגשות...',
                        operation: 'sentiment',
                    };
                },
            }),

            text_to_speech: tool({
                description: 'המר טקסט לדיבור. השתמש כשהמשתמש רוצה ליצור אודיו מטקסט.',
                parameters: z.object({
                    text: z.string().describe('הטקסט להמרה'),
                    language: z.string().default('he').describe('קוד שפה'),
                    voiceId: z.string().optional().describe('Voice ID לשיבוט קול'),
                }),
                execute: async ({ text, language, voiceId }) => {
                    return {
                        status: 'processing',
                        taskId: `task_${Date.now()}`,
                        message: `ממיר לדיבור: "${text.substring(0, 50)}..."`,
                        operation: 'tts',
                    };
                },
            }),
        },
    });

    return result.toDataStreamResponse();
}
