'use client';

import { Copy, Check } from 'lucide-react';
import { useState } from 'react';

interface TranscriptViewerProps {
    transcript: string;
    speakers?: Array<{ speaker: string; text: string; timestamp?: string }>;
    onDownload?: () => void;
}

export function TranscriptViewer({ transcript, speakers, onDownload }: TranscriptViewerProps) {
    const [copied, setCopied] = useState(false);

    const handleCopy = async () => {
        await navigator.clipboard.writeText(transcript);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
            {/* Header */}
            <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                    <span className="text-2xl">📝</span>
                    <h4 className="font-semibold text-slate-900 dark:text-slate-100">
                        תמלול
                    </h4>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={handleCopy}
                        className="px-3 py-1.5 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 rounded-lg transition-colors flex items-center gap-2 text-sm"
                    >
                        {copied ? (
                            <>
                                <Check className="w-4 h-4 text-green-500" />
                                <span className="text-green-500">הועתק!</span>
                            </>
                        ) : (
                            <>
                                <Copy className="w-4 h-4" />
                                <span>העתק</span>
                            </>
                        )}
                    </button>
                    {onDownload && (
                        <button
                            onClick={onDownload}
                            className="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors text-sm"
                        >
                            הורד TXT
                        </button>
                    )}
                </div>
            </div>

            {/* Transcript Content */}
            <div className="max-h-64 overflow-y-auto">
                {speakers && speakers.length > 0 ? (
                    // With speaker diarization
                    <div className="space-y-3">
                        {speakers.map((item, index) => (
                            <div key={index} className="flex gap-3">
                                <div className="flex-shrink-0">
                                    <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
                                        {item.speaker.slice(-1)}
                                    </div>
                                </div>
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className="text-xs font-semibold text-slate-900 dark:text-slate-100">
                                            {item.speaker}
                                        </span>
                                        {item.timestamp && (
                                            <span className="text-xs text-slate-500">
                                                {item.timestamp}
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-sm text-slate-700 dark:text-slate-300">
                                        {item.text}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    // Simple transcript
                    <p className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap leading-relaxed">
                        {transcript}
                    </p>
                )}
            </div>
        </div>
    );
}
