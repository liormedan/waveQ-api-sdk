'use client';

import { File, X, Music } from 'lucide-react';

interface UploadedFile {
    fileId: string;
    filename: string;
    size: number;
    type: string;
    url: string;
    uploadedAt: string;
}

interface FilePreviewProps {
    file: UploadedFile;
    onRemove?: () => void;
}

export function FilePreview({ file, onRemove }: FilePreviewProps) {
    const formatFileSize = (bytes: number) => {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    const getFileIcon = () => {
        if (file.type.includes('mp3') || file.type.includes('mpeg')) {
            return '🎵';
        }
        if (file.type.includes('wav')) {
            return '🎼';
        }
        if (file.type.includes('flac')) {
            return '🎹';
        }
        return '🎧';
    };

    return (
        <div className="group relative bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-4 hover:border-blue-500 dark:hover:border-blue-500 transition-all hover:shadow-md">
            <div className="flex items-start gap-3">
                {/* File Icon */}
                <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900/30 dark:to-purple-900/30 rounded-lg flex items-center justify-center text-2xl">
                        {getFileIcon()}
                    </div>
                </div>

                {/* File Info */}
                <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-slate-900 dark:text-slate-100 truncate">
                        {file.filename}
                    </h4>
                    <div className="mt-1 flex items-center gap-2 text-xs text-slate-600 dark:text-slate-400">
                        <span>{formatFileSize(file.size)}</span>
                        <span>•</span>
                        <span>{file.type.split('/')[1].toUpperCase()}</span>
                    </div>

                    {/* Audio Player */}
                    <div className="mt-3">
                        <audio
                            controls
                            className="w-full h-8 [&::-webkit-media-controls-panel]:bg-slate-100 dark:[&::-webkit-media-controls-panel]:bg-slate-700"
                            src={file.url}
                        >
                            הדפדפן שלך לא תומך בנגן אודיו
                        </audio>
                    </div>
                </div>

                {/* Remove Button */}
                {onRemove && (
                    <button
                        onClick={onRemove}
                        className="flex-shrink-0 p-1 rounded-lg hover:bg-red-50 dark:hover:bg-red-950/20 text-slate-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                        title="הסר קובץ"
                    >
                        <X className="w-5 h-5" />
                    </button>
                )}
            </div>

            {/* Success indicator */}
            <div className="absolute top-2 right-2 w-2 h-2 bg-green-500 rounded-full" />
        </div>
    );
}
