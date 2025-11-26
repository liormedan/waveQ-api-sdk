'use client';

import { useCallback, useState } from 'react';
import { Upload, File, X, Loader2 } from 'lucide-react';

interface UploadedFile {
    fileId: string;
    filename: string;
    size: number;
    type: string;
    url: string;
    uploadedAt: string;
}

interface FileUploadZoneProps {
    onFileUploaded: (file: UploadedFile) => void;
    maxSizeMB?: number;
}

export function FileUploadZone({ onFileUploaded, maxSizeMB = 100 }: FileUploadZoneProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [error, setError] = useState<string | null>(null);

    const handleUpload = useCallback(
        async (file: File) => {
            setError(null);
            setUploading(true);
            setUploadProgress(0);

            try {
                // Validate file type
                if (!file.type.startsWith('audio/')) {
                    throw new Error('רק קבצי אודיו מותרים');
                }

                // Validate file size
                if (file.size > maxSizeMB * 1024 * 1024) {
                    throw new Error(`הקובץ גדול מדי. מקסימום ${maxSizeMB}MB`);
                }

                const formData = new FormData();
                formData.append('file', file);

                // Simulate progress (in real app, use XMLHttpRequest for actual progress)
                const progressInterval = setInterval(() => {
                    setUploadProgress((prev) => Math.min(prev + 10, 90));
                }, 100);

                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData,
                });

                clearInterval(progressInterval);
                setUploadProgress(100);

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'העלאה נכשלה');
                }

                const uploadedFile: UploadedFile = await response.json();
                onFileUploaded(uploadedFile);

                setTimeout(() => {
                    setUploading(false);
                    setUploadProgress(0);
                }, 500);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'שגיאה בהעלאה');
                setUploading(false);
                setUploadProgress(0);
            }
        },
        [onFileUploaded, maxSizeMB]
    );

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback(
        (e: React.DragEvent) => {
            e.preventDefault();
            setIsDragging(false);

            const files = Array.from(e.dataTransfer.files);
            if (files.length > 0) {
                handleUpload(files[0]);
            }
        },
        [handleUpload]
    );

    const handleFileSelect = useCallback(
        (e: React.ChangeEvent<HTMLInputElement>) => {
            const files = e.target.files;
            if (files && files.length > 0) {
                handleUpload(files[0]);
            }
        },
        [handleUpload]
    );

    return (
        <div className="w-full">
            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`
          relative border-2 border-dashed rounded-xl p-8 text-center transition-all
          ${isDragging
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/20'
                        : 'border-slate-300 dark:border-slate-700 hover:border-blue-400 dark:hover:border-blue-600'
                    }
          ${uploading ? 'opacity-50 pointer-events-none' : 'cursor-pointer'}
        `}
            >
                <input
                    type="file"
                    accept="audio/*"
                    onChange={handleFileSelect}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    disabled={uploading}
                />

                {uploading ? (
                    <div className="space-y-4">
                        <Loader2 className="w-12 h-12 mx-auto text-blue-500 animate-spin" />
                        <div className="space-y-2">
                            <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                                מעלה קובץ...
                            </p>
                            <div className="max-w-xs mx-auto h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300"
                                    style={{ width: `${uploadProgress}%` }}
                                />
                            </div>
                            <p className="text-xs text-slate-500">{uploadProgress}%</p>
                        </div>
                    </div>
                ) : (
                    <div className="space-y-4">
                        <div className="flex justify-center">
                            <div className="p-4 bg-blue-100 dark:bg-blue-900/30 rounded-full">
                                <Upload className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                            </div>
                        </div>
                        <div>
                            <p className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                                גרור קובץ או לחץ להעלאה
                            </p>
                            <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                                MP3, WAV, FLAC, AAC (עד {maxSizeMB}MB)
                            </p>
                        </div>
                    </div>
                )}

                {error && (
                    <div className="mt-4 p-3 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800 rounded-lg">
                        <div className="flex items-center gap-2 text-red-700 dark:text-red-400">
                            <X className="w-4 h-4" />
                            <p className="text-sm">{error}</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
