'use client';

import { AudioPlayer } from './AudioPlayer';
import { TranscriptViewer } from './TranscriptViewer';
import { SentimentCard } from './SentimentCard';
import { Download, FileAudio } from 'lucide-react';

interface ProcessingResult {
    operation: string;
    taskId: string;
    audioUrl?: string;
    filename?: string;
    transcript?: string;
    speakers?: Array<{ speaker: string; text: string; timestamp?: string }>;
    sentiment?: {
        label: 'positive' | 'neutral' | 'negative';
        score: number;
        emotions?: Record<string, number>;
    };
    separatedFiles?: Array<{ type: string; url: string; filename: string }>;
}

interface ResultCardProps {
    result: ProcessingResult;
    onDownload?: (taskId: string, type: string) => void;
}

export function ResultCard({ result, onDownload }: ResultCardProps) {
    const getOperationTitle = (operation: string) => {
        const titles: Record<string, string> = {
            denoise: 'אודיו נקי',
            transcribe: 'תמלול',
            trim: 'אודיו חתוך',
            separate: 'קבצים מופרדים',
            sentiment: 'ניתוח סנטימנט',
            tts: 'דיבור מסונתז',
        };
        return titles[operation] || operation;
    };

    return (
        <div className="space-y-3">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                <span>✨</span>
                <span>{getOperationTitle(result.operation)}</span>
            </h3>

            {/* Audio Result */}
            {result.audioUrl && result.filename && (
                <AudioPlayer
                    url={result.audioUrl}
                    filename={result.filename}
                    onDownload={() => onDownload?.(result.taskId, 'audio')}
                />
            )}

            {/* Transcript Result */}
            {result.transcript && (
                <TranscriptViewer
                    transcript={result.transcript}
                    speakers={result.speakers}
                    onDownload={() => onDownload?.(result.taskId, 'transcript')}
                />
            )}

            {/* Sentiment Result */}
            {result.sentiment && (
                <SentimentCard
                    sentiment={result.sentiment.label}
                    score={result.sentiment.score}
                    emotions={result.sentiment.emotions}
                />
            )}

            {/* Separated Files */}
            {result.separatedFiles && result.separatedFiles.length > 0 && (
                <div className="space-y-2">
                    {result.separatedFiles.map((file, index) => (
                        <div
                            key={index}
                            className="flex items-center justify-between p-3 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700"
                        >
                            <div className="flex items-center gap-3">
                                <FileAudio className="w-5 h-5 text-blue-500" />
                                <div>
                                    <p className="font-medium text-slate-900 dark:text-slate-100 text-sm">
                                        {file.type}
                                    </p>
                                    <p className="text-xs text-slate-500">{file.filename}</p>
                                </div>
                            </div>
                            <button
                                onClick={() => onDownload?.(result.taskId, file.type)}
                                className="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors flex items-center gap-2 text-sm"
                            >
                                <Download className="w-4 h-4" />
                                <span>הורד</span>
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
