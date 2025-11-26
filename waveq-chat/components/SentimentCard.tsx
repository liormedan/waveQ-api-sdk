'use client';

import { Smile, Meh, Frown } from 'lucide-react';

interface SentimentCardProps {
    sentiment: 'positive' | 'neutral' | 'negative';
    score: number;
    emotions?: Record<string, number>;
}

export function SentimentCard({ sentiment, score, emotions }: SentimentCardProps) {
    const getSentimentIcon = () => {
        switch (sentiment) {
            case 'positive':
                return <Smile className="w-6 h-6 text-green-500" />;
            case 'neutral':
                return <Meh className="w-6 h-6 text-slate-500" />;
            case 'negative':
                return <Frown className="w-6 h-6 text-red-500" />;
        }
    };

    const getSentimentColor = () => {
        switch (sentiment) {
            case 'positive':
                return 'from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20 border-green-200 dark:border-green-800';
            case 'neutral':
                return 'from-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-900 border-slate-200 dark:border-slate-700';
            case 'negative':
                return 'from-red-50 to-rose-50 dark:from-red-950/20 dark:to-rose-950/20 border-red-200 dark:border-red-800';
        }
    };

    const getSentimentLabel = () => {
        switch (sentiment) {
            case 'positive':
                return 'חיובי';
            case 'neutral':
                return 'נייטרלי';
            case 'negative':
                return 'שלילי';
        }
    };

    const getEmotionEmoji = (emotion: string) => {
        const emojiMap: Record<string, string> = {
            joy: '😊',
            sadness: '😢',
            anger: '😠',
            fear: '😨',
            surprise: '😮',
            love: '❤️',
            excitement: '🎉',
        };
        return emojiMap[emotion] || '😐';
    };

    const getEmotionLabel = (emotion: string) => {
        const labelMap: Record<string, string> = {
            joy: 'שמחה',
            sadness: 'עצב',
            anger: 'כעס',
            fear: 'פחד',
            surprise: 'הפתעה',
            love: 'אהבה',
            excitement: 'התרגשות',
        };
        return labelMap[emotion] || emotion;
    };

    return (
        <div className={`bg-gradient-to-br ${getSentimentColor()} rounded-xl border p-4`}>
            {/* Header */}
            <div className="flex items-center gap-3 mb-3">
                <div className="flex-shrink-0">
                    {getSentimentIcon()}
                </div>
                <div className="flex-1">
                    <h4 className="font-semibold text-slate-900 dark:text-slate-100">
                        סנטימנט: {getSentimentLabel()}
                    </h4>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                        ביטחון: {Math.round(score * 100)}%
                    </p>
                </div>
            </div>

            {/* Progress Bar */}
            <div className="mb-4">
                <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                    <div
                        className={`h-full transition-all ${sentiment === 'positive'
                                ? 'bg-green-500'
                                : sentiment === 'negative'
                                    ? 'bg-red-500'
                                    : 'bg-slate-500'
                            }`}
                        style={{ width: `${score * 100}%` }}
                    />
                </div>
            </div>

            {/* Emotions */}
            {emotions && Object.keys(emotions).length > 0 && (
                <div>
                    <h5 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                        רגשות שזוהו:
                    </h5>
                    <div className="flex flex-wrap gap-2">
                        {Object.entries(emotions)
                            .sort(([, a], [, b]) => b - a)
                            .slice(0, 5)
                            .map(([emotion, value]) => (
                                <div
                                    key={emotion}
                                    className="px-3 py-1.5 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 flex items-center gap-2"
                                >
                                    <span className="text-lg">{getEmotionEmoji(emotion)}</span>
                                    <span className="text-sm text-slate-700 dark:text-slate-300">
                                        {getEmotionLabel(emotion)}
                                    </span>
                                    <span className="text-xs text-slate-500">
                                        {Math.round(value * 100)}%
                                    </span>
                                </div>
                            ))}
                    </div>
                </div>
            )}
        </div>
    );
}
