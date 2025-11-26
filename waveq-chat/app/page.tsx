'use client';

import { useChat } from 'ai/react';
import { Send, Loader2, Upload, Paperclip, Trash2 } from 'lucide-react';
import { useState } from 'react';
import { FileUploadZone } from '@/components/FileUploadZone';
import { FilePreview } from '@/components/FilePreview';
import { TaskProgress } from '@/components/TaskProgress';
import { ResultCard } from '@/components/ResultCard';
import { useFileManagement, UploadedFile } from '@/lib/hooks/useFileManagement';

export default function Chat() {
    const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat();
    const { files, currentFile, addFile, removeFile, clearFiles } = useFileManagement();
    const [showUpload, setShowUpload] = useState(false);

    const handleFileUploaded = (file: UploadedFile) => {
        addFile(file);
        setShowUpload(false);
    };

    const handleDownload = async (taskId: string, type: string) => {
        try {
            const response = await fetch(`/api/download/${taskId}?type=${type}`);
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${taskId}_${type}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            }
        } catch (error) {
            console.error('Download failed:', error);
        }
    };

    // Parse results from messages
    const getResultsFromMessage = (message: any) => {
        if (!message.toolInvocations) return null;

        // Check if all tools completed
        const allCompleted = message.toolInvocations.every(
            (tool: any) => tool.state === 'result'
        );

        if (!allCompleted) return null;

        // Extract results
        const results = message.toolInvocations
            .map((tool: any) => {
                if (!tool.result) return null;
                const result = typeof tool.result === 'string' ? JSON.parse(tool.result) : tool.result;

                // Mock data for demonstration
                if (result.operation === 'denoise') {
                    return {
                        operation: 'denoise',
                        taskId: result.taskId,
                        audioUrl: '/demo/cleaned_audio.wav',
                        filename: 'audio_cleaned.wav',
                    };
                }

                if (result.operation === 'transcribe') {
                    return {
                        operation: 'transcribe',
                        taskId: result.taskId,
                        transcript: 'זהו תמלול לדוגמה של האודיו. בפועל, כאן יופיע התמלול האמיתי מה-API של WaveQ עם Whisper. התמלול יכלול את כל הדיבור שזוהה בקובץ.',
                        speakers: [
                            { speaker: 'Speaker 1', text: 'שלום לכולם, היום נדבר על...', timestamp: '00:00' },
                            { speaker: 'Speaker 2', text: 'מעולה, אני מאוד שמח להיות כאן', timestamp: '00:15' },
                        ],
                    };
                }

                if (result.operation === 'sentiment') {
                    return {
                        operation: 'sentiment',
                        taskId: result.taskId,
                        sentiment: {
                            label: 'positive' as const,
                            score: 0.85,
                            emotions: {
                                joy: 0.7,
                                excitement: 0.5,
                                love: 0.3,
                            },
                        },
                    };
                }

                return result;
            })
            .filter((r: any) => r !== null);

        return results.length > 0 ? results : null;
    };

    return (
        <div className="flex flex-col h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800" dir="rtl">
            {/* Header */}
            <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 px-6 py-4">
                <div className="max-w-4xl mx-auto flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                            🎙️ WaveQ Audio Agent
                        </h1>
                        <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                            סוכן AI לעיבוד אודיו - שיחה טבעית, עריכה חכמה
                        </p>
                    </div>
                    {files.length > 0 && (
                        <div className="flex items-center gap-3">
                            <div className="text-sm text-slate-600 dark:text-slate-400">
                                {files.length} {files.length === 1 ? 'קובץ' : 'קבצים'}
                            </div>
                            <button
                                onClick={clearFiles}
                                className="px-3 py-2 text-sm text-slate-600 dark:text-slate-400 hover:text-red-600 dark:hover:text-red-400 transition-colors flex items-center gap-2"
                            >
                                <Trash2 className="w-4 h-4" />
                                נקה
                            </button>
                        </div>
                    )}
                </div>
            </header>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-4 py-6">
                <div className="max-w-4xl mx-auto space-y-6">
                    {messages.length === 0 && files.length === 0 && (
                        <div className="text-center py-12">
                            <div className="text-6xl mb-4">🎵</div>
                            <h2 className="text-xl font-semibold text-slate-700 dark:text-slate-300 mb-2">
                                ברוכים הבאים ל-WaveQ!
                            </h2>
                            <p className="text-slate-600 dark:text-slate-400 mb-6">
                                העלה קובץ אודיו ושאל אותי מה לעשות - אני אעזור לך לערוך ולנתח
                            </p>

                            <button
                                onClick={() => setShowUpload(true)}
                                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all hover:shadow-lg inline-flex items-center gap-2 mb-8"
                            >
                                <Upload className="w-5 h-5" />
                                <span>העלה קובץ אודיו</span>
                            </button>

                            <div className="mt-8 grid grid-cols-2 md:grid-cols-3 gap-3 max-w-2xl mx-auto">
                                {[
                                    { icon: '🎤', text: 'תמלול דיבור', desc: 'המר דיבור לטקסט' },
                                    { icon: '🔇', text: 'הסרת רעש', desc: 'נקה אודיו מרעש' },
                                    { icon: '✂️', text: 'חיתוך שקט', desc: 'הסר חלקים שקטים' },
                                    { icon: '🎼', text: 'הפרדת ווקלים', desc: 'בודד ווקלים ממוזיקה' },
                                    { icon: '😊', text: 'ניתוח רגשות', desc: 'זהה סנטימנט' },
                                    { icon: '🗣️', text: 'טקסט לדיבור', desc: 'צור אודיו מטקסט' },
                                ].map((action, i) => (
                                    <div
                                        key={i}
                                        className="p-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-blue-500 dark:hover:border-blue-500 transition-all hover:shadow-md text-center"
                                    >
                                        <div className="text-4xl mb-2">{action.icon}</div>
                                        <div className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-1">
                                            {action.text}
                                        </div>
                                        <div className="text-xs text-slate-500">
                                            {action.desc}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Uploaded Files */}
                    {files.length > 0 && (
                        <div className="space-y-2">
                            <h3 className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-2">
                                📎 קבצים ({files.length})
                            </h3>
                            {files.map((file) => (
                                <FilePreview
                                    key={file.fileId}
                                    file={file}
                                    onRemove={() => removeFile(file.fileId)}
                                />
                            ))}
                        </div>
                    )}

                    {/* Upload Zone */}
                    {showUpload && (
                        <div className="animate-in fade-in slide-in-from-bottom-4 duration-300">
                            <FileUploadZone onFileUploaded={handleFileUploaded} />
                        </div>
                    )}

                    {/* Messages */}
                    {messages.map((message) => {
                        const results = getResultsFromMessage(message);

                        return (
                            <div key={message.id} className="space-y-4">
                                {/* User/AI Message */}
                                <div className={`flex ${message.role === 'user' ? 'justify-start' : 'justify-end'}`}>
                                    <div
                                        className={`max-w-[85%] rounded-2xl px-5 py-3 ${message.role === 'user'
                                                ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 border border-slate-200 dark:border-slate-700'
                                                : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                                            }`}
                                    >
                                        <div className="flex items-start gap-3">
                                            <span className="text-xl flex-shrink-0">
                                                {message.role === 'user' ? '👤' : '🤖'}
                                            </span>
                                            <div className="flex-1 min-w-0">
                                                <div className="whitespace-pre-wrap leading-relaxed">{message.content}</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Task Progress */}
                                {message.toolInvocations && message.toolInvocations.length > 0 && !results && (
                                    <div className="space-y-2 pr-12">
                                        {message.toolInvocations.map((tool) => {
                                            const result = tool.result ? (typeof tool.result === 'string' ? JSON.parse(tool.result) : tool.result) : null;
                                            if (result && result.operation) {
                                                return (
                                                    <TaskProgress
                                                        key={tool.toolCallId}
                                                        taskId={result.taskId || tool.toolCallId}
                                                        operation={result.operation}
                                                        status={tool.state === 'result' ? 'completed' : 'processing'}
                                                        progress={tool.state === 'result' ? 100 : 50}
                                                        message={result.message}
                                                    />
                                                );
                                            }
                                            return null;
                                        })}
                                    </div>
                                )}

                                {/* Results */}
                                {results && results.length > 0 && (
                                    <div className="pr-12 space-y-4">
                                        {results.map((result: any, idx: number) => (
                                            <ResultCard
                                                key={idx}
                                                result={result}
                                                onDownload={handleDownload}
                                            />
                                        ))}
                                    </div>
                                )}
                            </div>
                        );
                    })}

                    {isLoading && (
                        <div className="flex justify-end">
                            <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl px-5 py-3 shadow-lg">
                                <div className="flex items-center gap-2">
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    <span>חושב...</span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Input Area */}
            <div className="bg-white dark:bg-slate-800 border-t border-slate-200 dark:border-slate-700 px-4 py-4 shadow-lg">
                <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
                    <div className="flex gap-2">
                        <button
                            type="button"
                            onClick={() => setShowUpload(!showUpload)}
                            className={`px-4 py-3 rounded-xl transition-all flex-shrink-0 ${showUpload
                                    ? 'bg-blue-500 text-white shadow-md'
                                    : 'bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600'
                                }`}
                            title="העלה קובץ"
                        >
                            {showUpload ? <Paperclip className="w-5 h-5" /> : <Upload className="w-5 h-5" />}
                        </button>
                        <input
                            value={input}
                            onChange={handleInputChange}
                            placeholder={
                                files.length > 0
                                    ? "מה תרצה לעשות? (למשל: 'תנקה ותמלל')"
                                    : "שאל אותי על עיבוד אודיו או העלה קובץ..."
                            }
                            className="flex-1 px-5 py-3 bg-slate-100 dark:bg-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-900 dark:text-slate-100 placeholder:text-slate-500"
                            disabled={isLoading}
                        />
                        <button
                            type="submit"
                            disabled={isLoading || !input.trim()}
                            className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:shadow-lg flex-shrink-0"
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Quick suggestions when files are uploaded */}
                    {files.length > 0 && !isLoading && (
                        <div className="mt-3 flex flex-wrap gap-2">
                            {[
                                'תנקה רעש',
                                'תמלל',
                                'תנקה ותמלל',
                                'הפרד ווקלים',
                                'נתח סנטימנט',
                            ].map((suggestion, i) => (
                                <button
                                    key={i}
                                    type="button"
                                    onClick={() => {
                                        const inputEl = document.querySelector('input[type="text"]') as HTMLInputElement;
                                        if (inputEl) {
                                            inputEl.value = suggestion;
                                            inputEl.focus();
                                        }
                                    }}
                                    className="px-3 py-1.5 text-sm bg-slate-100 dark:bg-slate-700 hover:bg-blue-100 dark:hover:bg-blue-900/30 text-slate-700 dark:text-slate-300 rounded-lg transition-colors"
                                >
                                    {suggestion}
                                </button>
                            ))}
                        </div>
                    )}
                </form>
            </div>
        </div>
    );
}
