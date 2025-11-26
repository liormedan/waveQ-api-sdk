'use client';

import { Loader2, CheckCircle2, XCircle, Clock } from 'lucide-react';

export type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed';

interface TaskProgressProps {
    taskId: string;
    operation: string;
    status: TaskStatus;
    progress?: number;
    message?: string;
    error?: string;
}

export function TaskProgress({ taskId, operation, status, progress = 0, message, error }: TaskProgressProps) {
    const getStatusIcon = () => {
        switch (status) {
            case 'pending':
                return <Clock className="w-5 h-5 text-slate-400" />;
            case 'processing':
                return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
            case 'completed':
                return <CheckCircle2 className="w-5 h-5 text-green-500" />;
            case 'failed':
                return <XCircle className="w-5 h-5 text-red-500" />;
        }
    };

    const getStatusColor = () => {
        switch (status) {
            case 'pending':
                return 'bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-slate-700';
            case 'processing':
                return 'bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800';
            case 'completed':
                return 'bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800';
            case 'failed':
                return 'bg-red-50 dark:bg-red-950/20 border-red-200 dark:border-red-800';
        }
    };

    const getOperationEmoji = (op: string) => {
        const emojiMap: Record<string, string> = {
            denoise: '🔇',
            transcribe: '📝',
            trim: '✂️',
            separate: '🎼',
            sentiment: '😊',
            tts: '🗣️',
        };
        return emojiMap[op] || '🎵';
    };

    const getOperationName = (op: string) => {
        const nameMap: Record<string, string> = {
            denoise: 'ניקוי רעש',
            transcribe: 'תמלול',
            trim: 'חיתוך',
            separate: 'הפרדה',
            sentiment: 'ניתוח סנטימנט',
            tts: 'המרה לדיבור',
        };
        return nameMap[op] || op;
    };

    return (
        <div className={`border rounded-xl p-4 ${getStatusColor()}`}>
            <div className="flex items-start gap-3">
                {/* Icon */}
                <div className="flex-shrink-0 mt-0.5">
                    {getStatusIcon()}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                        <span className="text-lg">{getOperationEmoji(operation)}</span>
                        <h4 className="font-medium text-slate-900 dark:text-slate-100">
                            {getOperationName(operation)}
                        </h4>
                    </div>

                    {message && (
                        <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                            {message}
                        </p>
                    )}

                    {error && (
                        <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                            {error}
                        </p>
                    )}

                    {/* Progress Bar */}
                    {status === 'processing' && progress > 0 && (
                        <div className="mt-3">
                            <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300"
                                    style={{ width: `${progress}%` }}
                                />
                            </div>
                            <p className="mt-1 text-xs text-slate-500">{progress}%</p>
                        </div>
                    )}
                </div>

                {/* Task ID (for debugging) */}
                {status === 'completed' && (
                    <div className="text-xs text-slate-400 font-mono">
                        #{taskId.slice(0, 8)}
                    </div>
                )}
            </div>
        </div>
    );
}
